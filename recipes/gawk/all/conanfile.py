from conan import ConanFile
from conan.tools.files import copy, get, collect_libs
from conan.tools.layout import basic_layout
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
import os

required_conan_version = ">=1.52.0"


class GawkConan(ConanFile):
    name = "gawk"
    description = "A program that you can use to select particular records in a file and perform operations upon them. GNU implementation of awk"
    topics = ("file", "modification", "reformatting")
    homepage = "http://git.savannah.gnu.org/cgit/gawk.git"
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def configure(self):
        # This is a C library. Remove C++ metadata
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def compatibility(self):
        return [{"settings": [("build_type", "Release")]}]

    def validate(self):
        pass

    def requirements(self):
        #self.requires("mpfr/4.1.0")
        self.requires("gmp/6.2.1")

        # Removed pending readline conan 2.0 compatibility
        # if self.settings.os == "Macos":
        #     self.requires("readline/8.1.2")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.24")
        else:
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.8.2")
            self.tool_requires("binutils/2.38")
            self.tool_requires("libtool/2.4.7")
            # self.tool_requires("grep/3.10")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append(f"--with-gmp={self.dependencies['gmp'].package_folder}")
        #tc.configure_args.append(f"--with-mpc={self.dependencies['mpc'].package_folder}")
        #tc.configure_args.append(f"--with-mpfr={self.dependencies['mpfr'].package_folder}")

        # Removed pending readline conan 2.0 compatibility
        # if self.settings.os == "Macos":
        #     tc.configure_args.append(f"--with-readline={self.dependencies['readline'].package_folder}")

        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.resdirs = ["share"]
        collect_libs(self)

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
