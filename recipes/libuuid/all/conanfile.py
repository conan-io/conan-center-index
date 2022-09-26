from conan import ConanFile
from conan.tools.files import export_conandata_patches, apply_conandata_patches, get, rm , rmdir, copy
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.build import cross_building
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"


class LibuuidConan(ConanFile):
    name = "libuuid"
    description = "Portable uuid C library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/libuuid/"
    license = "BSD-3-Clause"
    topics = ("conan", "libuuid", "uuid", "unique-id", "unique-identifier")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        basic_layout(self)

    def validate(self):
        if self.info.settings.os == "Windows":
            raise ConanInvalidConfiguration("libuuid is not supported on Windows")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        if "x86" in self.settings.arch:
            tc.extra_cflags = ['-mstackrealign']
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "uuid")
        self.cpp_info.libs = ["uuid"]
        self.cpp_info.includedirs.append(os.path.join("include", "uuid"))
