from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, mkdir, rename, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.47.0"


class UncrustifyConan(ConanFile):
    name = "uncrustify"
    description = "Code beautifier"
    license = "GPL-2.0-or-later"
    topics = "beautifier", "command-line"
    homepage = "https://github.com/uncrustify/uncrustify"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration(f"{self.ref} requires GCC >=7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NoGitVersionString"] = True
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

        if is_msvc(self):
            mkdir(self, os.path.join(self.package_folder, "bin"))
            rename(self, os.path.join(self.package_folder, "uncrustify.exe"),
                         os.path.join(self.package_folder, "bin", "uncrustify.exe"))
            os.remove(os.path.join(self.package_folder, "AUTHORS"))
            os.remove(os.path.join(self.package_folder, "BUGS"))
            os.remove(os.path.join(self.package_folder, "COPYING"))
            os.remove(os.path.join(self.package_folder, "ChangeLog"))
            os.remove(os.path.join(self.package_folder, "HELP"))
            os.remove(os.path.join(self.package_folder, "README.md"))
            rmdir(self, os.path.join(self.package_folder, "cfg"))
            rmdir(self, os.path.join(self.package_folder, "doc"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2
        binpath = os.path.join(self.package_folder, "bin")
        self.output.info(f"Adding to PATH: {binpath}")
        self.env_info.PATH.append(binpath)
