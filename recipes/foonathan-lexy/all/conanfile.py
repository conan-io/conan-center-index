from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class FoonathanLexyConan(ConanFile):
    name = "foonathan-lexy"
    description = "lexy is a parser combinator library for C++17 and onwards."
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/foonathan/lexy"
    topics = ("parser", "parser-combinators", "grammar")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.18 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LEXY_BUILD_EXAMPLES"] = False
        tc.variables["LEXY_BUILD_TESTS"] = False
        tc.variables["LEXY_BUILD_PACKAGE"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "lexy")
        self.cpp_info.set_property("cmake_target_name", "foonathan::lexy")

        self.cpp_info.components["lexy_core"].set_property("cmake_target_name", "foonathan::lexy::lexy_core")

        self.cpp_info.components["lexy_file"].set_property("cmake_target_name", "foonathan::lexy::lexy_file")
        self.cpp_info.components["lexy_file"].libs = ["lexy_file"]

        self.cpp_info.components["lexy_unicode"].set_property("cmake_target_name", "lexy::lexy_unicode")
        self.cpp_info.components["lexy_unicode"].defines.append("LEXY_HAS_UNICODE_DATABASE=1")

        self.cpp_info.components["lexy_ext"].set_property("cmake_target_name", "lexy::lexy_ext")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "lexy"
        self.cpp_info.filenames["cmake_find_package_multi"] = "lexy"
        self.cpp_info.names["cmake_find_package"] = "foonathan"
        self.cpp_info.names["cmake_find_package_multi"] = "foonathan"
        self.cpp_info.components["foonathan"].names["cmake_find_package"] = "lexy"
        self.cpp_info.components["foonathan"].names["cmake_find_package_multi"] = "lexy"
