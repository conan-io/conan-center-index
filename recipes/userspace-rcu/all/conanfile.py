from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir, chdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.apple import is_apple_os
import os

required_conan_version = ">=1.54.0"

class UserspaceRCUConan(ConanFile):
    name = "userspace-rcu"
    description = "Userspace RCU (read-copy-update) library"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage ="https://liburcu.org/"
    topics = ("urcu")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"] and not is_apple_os(self):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support {self.settings.os} building")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = AutotoolsToolchain(self)
        tc.generate()
        pkgdeps = PkgConfigDeps(self)
        pkgdeps.generate()
        autodeps = AutotoolsDeps(self)
        autodeps.generate()

    def build(self):
        with chdir(self, self.source_folder):
            self.run("./bootstrap")
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        for lib_type in ["", "-bp", "-cds", "-mb", "-memb", "-qsbr", "-signal"]:
            component_name = "urcu{}".format(lib_type)
            self.cpp_info.components[component_name].libs = ["urcu-common", component_name]
            self.cpp_info.components[component_name].set_property("pkg_config_name", component_name)
            if self.settings.os == "Linux":
                self.cpp_info.components[component_name].system_libs = ["pthread"]

        # Some definitions needed for MB and Signal variants
        self.cpp_info.components["urcu-mb"].defines = ["RCU_MB"]
        self.cpp_info.components["urcu-signal"].defines = ["RCU_SIGNAL"]
