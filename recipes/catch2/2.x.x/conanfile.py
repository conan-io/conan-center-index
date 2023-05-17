from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class Catch2Conan(ConanFile):
    name = "catch2"
    description = "A modern, C++-native, header-only, framework for unit-tests, TDD and BDD"
    topics = ("header-only", "unit-test", "tdd", "bdd")
    homepage = "https://github.com/catchorg/Catch2"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_main": [True, False],
        "with_benchmark": [True, False],
        "with_prefix": [True, False],
        "default_reporter": [None, "ANY"],
    }
    default_options = {
        "fPIC": True,
        "with_main": False,
        "with_benchmark": False,
        "with_prefix": False,
        "default_reporter": None,
    }

    @property
    def _default_reporter_str(self):
        return str(self.options.default_reporter).strip('"')

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if not self.options.with_main:
            self.options.rm_safe("fPIC")
            self.options.rm_safe("with_benchmark")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if not self.info.options.with_main:
            self.info.clear()

    def validate(self):
        if Version(self.version) < "2.13.1" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("ARMv8 is not supported by versions < 2.13.1+")
        if self.options.get_safe("with_main") and Version(self.version) < "2.13.4":
            raise ConanInvalidConfiguration("Option with_main not supported by versions < 2.13.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.cache_variables["CATCH_INSTALL_DOCS"] = False    # these are cmake options, so use cache_variables
        tc.cache_variables["CATCH_INSTALL_HELPERS"] = "ON"  # these are cmake options, so use cache_variables
        tc.cache_variables["CATCH_BUILD_STATIC_LIBRARY"] = str(self.options.with_main)   # these are cmake options, so use cache_variables (str() is required for conan 1.52)
        if self.options.with_prefix:
            tc.preprocessor_definitions["CATCH_CONFIG_PREFIX_ALL"] = 1
        if self.options.get_safe("with_benchmark", False):
            tc.preprocessor_definitions["CATCH_CONFIG_ENABLE_BENCHMARKING"] = 1
        if self.options.default_reporter:
            tc.variables["CATCH_CONFIG_DEFAULT_REPORTER"] = self._default_reporter_str
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        if self.options.with_main:
            cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        for cmake_file in ["ParseAndAddCatchTests.cmake", "Catch.cmake", "CatchAddTests.cmake"]:
            copy(self,
                cmake_file,
                src=os.path.join(self.source_folder, "contrib"),
                dst=os.path.join(self.package_folder, "lib", "cmake", "Catch2"),
            )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Catch2")
        self.cpp_info.set_property("cmake_target_name", "Catch2::Catch2{}".format("WithMain" if self.options.with_main else ""))
        self.cpp_info.set_property("pkg_config_name", "catch2{}".format("-with-main" if self.options.with_main else ""))

        defines = []
        if self.options.get_safe("with_benchmark", False):
            defines.append("CATCH_CONFIG_ENABLE_BENCHMARKING")
        if self.options.with_prefix:
            defines.append("CATCH_CONFIG_PREFIX_ALL")
        if self.options.default_reporter:
            defines.append(f"CATCH_CONFIG_DEFAULT_REPORTER={self._default_reporter_str}")

        if self.options.with_main:
            self.cpp_info.components["_catch2"].set_property("cmake_target_name", "Catch2::Catch2")
            self.cpp_info.components["_catch2"].set_property("pkg_config_name", "catch2")
            self.cpp_info.components["_catch2"].defines = defines

            self.cpp_info.components["catch2_with_main"].builddirs.append(os.path.join("lib", "cmake", "Catch2"))
            self.cpp_info.components["catch2_with_main"].libs = ["Catch2WithMain"]
            self.cpp_info.components["catch2_with_main"].system_libs = ["log"] if self.settings.os == "Android" else []
            self.cpp_info.components["catch2_with_main"].set_property("cmake_target_name", "Catch2::Catch2WithMain")
            self.cpp_info.components["catch2_with_main"].set_property("pkg_config_name", "catch2-with-main")
            self.cpp_info.components["catch2_with_main"].defines = defines
        else:
            self.cpp_info.builddirs = [os.path.join("lib", "cmake", "Catch2")]
            self.cpp_info.system_libs = ["log"] if self.settings.os == "Android" else []
            self.cpp_info.defines = defines

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "Catch2"
        self.cpp_info.names["cmake_find_package_multi"] = "Catch2"
        if self.options.with_main:
            self.cpp_info.components["_catch2"].names["cmake_find_package"] = "Catch2"
            self.cpp_info.components["_catch2"].names["cmake_find_package_multi"] = "Catch2"
            self.cpp_info.components["catch2_with_main"].names["cmake_find_package"] = "Catch2WithMain"
            self.cpp_info.components["catch2_with_main"].names["cmake_find_package_multi"] = "Catch2WithMain"
