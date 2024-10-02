import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class UserspaceRCUConan(ConanFile):
    name = "userspace-rcu"
    description = "Userspace RCU (read-copy-update) library"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://liburcu.org/"
    topics = "urcu"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD", "Macos"]:
            raise ConanInvalidConfiguration(f"Building for {self.settings.os} unsupported")
        if self.version == "0.11.4" and self.settings.compiler == "apple-clang":
            # Fails with "cds_hlist_add_head_rcu.c:19:10: fatal error: 'urcu/urcu-memb.h' file not found"
            raise ConanInvalidConfiguration(f"{self.ref} is not compatible with apple-clang")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE*",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", self.package_folder, recursive=True)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        for lib_type in ["", "-bp", "-cds", "-mb", "-memb", "-qsbr", "-signal"]:
            component_name = f"urcu{lib_type}"
            self.cpp_info.components[component_name].libs = ["urcu-common", component_name]
            self.cpp_info.components[component_name].set_property("pkg_config_name", component_name)
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components[component_name].system_libs = ["pthread"]

        # Some definitions needed for MB and Signal variants
        self.cpp_info.components["urcu-mb"].defines = ["RCU_MB"]
        self.cpp_info.components["urcu-signal"].defines = ["RCU_SIGNAL"]
