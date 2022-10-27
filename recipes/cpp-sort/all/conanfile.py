import os.path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.50.0"


class CppSortConan(ConanFile):
    name = "cpp-sort"
    description = "Additional sorting algorithms & related tools"
    topics = "conan", "cpp-sort", "sorting", "algorithms"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Morwenn/cpp-sort"
    license = "MIT"
    no_copy_source = True
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "apple-clang": "9.4",
            "clang": "3.8",
            "gcc": "5.5",
            "Visual Studio": "16"
        }

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        compiler = self.settings.compiler
        try:
            min_version = self._minimum_compilers_version[str(compiler)]
            if Version(compiler.version) < min_version:
                msg = (
                    "{} requires C++{} features which are not supported by compiler {} {}."
                ).format(self.name, self._minimum_cpp_standard, compiler, compiler.version)
                raise ConanInvalidConfiguration(msg)
        except KeyError:
            msg = (
                "{} recipe lacks information about the {} compiler, "
                "support for the required C++{} features is assumed"
            ).format(self.name, compiler, self._minimum_cpp_standard)
            self.output.warn(msg)

    def layout(self):
        cmake_layout(self, src_folder="source")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = "OFF"
        tc.generate()

    def package(self):
        # Install with CMake
        cmake = CMake(self)
        cmake.configure()
        cmake.install()

        # Copy license files
        if Version(self.version) < "1.8.0":
            license_files = ["license.txt"]
        else:
            license_files = ["LICENSE.txt", "NOTICE.txt"]
        for license_file in license_files:
            copy(self, license_file, self.source_folder, os.path.join(self.package_folder, "licenses"))

        # Remove CMake config files (only files in lib)
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "cpp-sort"
        self.cpp_info.names["cmake_find_package_multi"] = "cpp-sort"
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.cxxflags = ["/permissive-"]

    def package_id(self):
        self.info.clear()
