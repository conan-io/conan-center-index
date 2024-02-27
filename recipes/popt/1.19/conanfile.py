from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import collect_libs, copy, get, rmdir, rm
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=1.54.0"

class PoptConan(ConanFile):
    name = "popt"
    description = "Library for parsing command line parameters"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rpm-software-management/popt"
    topics = ("command line", "options", "parsing")
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        if self.settings.os == "Neutrino":
            self.requires("libiconv/1.15")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} can not be built with shared on Visual Studio and msvc, use mingw.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        ad = AutotoolsDeps(self)
        ad.generate()

        tc = AutotoolsToolchain(self)
        tc.ldflags.append("-lintl")
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        if is_apple_os(self):
            self.cpp_info.system_libs = ["iconv"]

        if self.settings.os == "Neutrino":
            self.cpp_info.system_libs = ["intl"]
