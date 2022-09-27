from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


class Catch2Conan(ConanFile):
    name = "catch2"
    description = "A modern, C++-native, header-only, framework for unit-tests, TDD and BDD"
    topics = ("catch2", "unit-test", "tdd", "bdd")
    license = "BSL-1.0"
    homepage = "https://github.com/catchorg/Catch2"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_prefix": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_prefix": False,
    }

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15",
            "msvc": "191",
            "clang": "5",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

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
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler doesn't support",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["CATCH_INSTALL_DOCS"] = False
        tc.variables["CATCH_INSTALL_HELPERS"] = True
        tc.variables["CATCH_CONFIG_PREFIX_ALL"] = self.options.with_prefix
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        for cmake_file in ["ParseAndAddCatchTests.cmake", "Catch.cmake", "CatchAddTests.cmake"]:
            copy(
                self,
                cmake_file,
                src=os.path.join(self.source_folder, "extras"),
                dst=os.path.join(self.package_folder, "lib", "cmake", "Catch2"),
            )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Catch2")
        self.cpp_info.set_property("cmake_target_name", "Catch2::Catch2WithMain")
        self.cpp_info.set_property("pkg_config_name", "catch2-with-main")

        lib_suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.components["_catch2"].set_property("cmake_target_name", "Catch2::Catch2")
        self.cpp_info.components["_catch2"].set_property("pkg_config_name", "catch2")
        self.cpp_info.components["_catch2"].libs = ["Catch2" + lib_suffix]

        self.cpp_info.components["catch2_with_main"].builddirs.append[os.path.join("lib", "cmake", "Catch2")]
        self.cpp_info.components["catch2_with_main"].libs = ["Catch2Main" + lib_suffix]
        self.cpp_info.components["catch2_with_main"].requires = ["_catch2"]
        self.cpp_info.components["catch2_with_main"].system_libs = ["log"] if self.settings.os == "Android" else []
        self.cpp_info.components["catch2_with_main"].set_property("cmake_target_name", "Catch2::Catch2WithMain")
        self.cpp_info.components["catch2_with_main"].set_property("pkg_config_name", "catch2-with-main")
        if self.options.with_prefix:
            self.cpp_info.components["catch2_with_main"].defines.append("CATCH_CONFIG_PREFIX_ALL")

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "Catch2"
        self.cpp_info.names["cmake_find_package_multi"] = "Catch2"
        self.cpp_info.components["_catch2"].names["cmake_find_package"] = "Catch2"
        self.cpp_info.components["_catch2"].names["cmake_find_package_multi"] = "Catch2"
        self.cpp_info.components["catch2_with_main"].names["cmake_find_package"] = "Catch2WithMain"
        self.cpp_info.components["catch2_with_main"].names["cmake_find_package_multi"] = "Catch2WithMain"
