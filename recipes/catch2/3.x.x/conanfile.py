import os
import functools
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.files import get, patch, rmdir

required_conan_version = ">=1.51.3"

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
        "default_reporter": "ANY",
    }
    default_options = {
        "fPIC": True,
        "with_prefix": False,
        "default_reporter": None,
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _default_reporter_str(self):
        return '"{}"'.format(str(self.options.default_reporter).strip('"'))

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15",
            "clang": "5",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "14")
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{}/{}: Unsupported compiler: {}-{} "
                                                "(https://github.com/p-ranav/structopt#compiler-compatibility)."
                                                .format(self.name, self.version, self.settings.compiler, self.settings.compiler.version))
        else:
            self.output.warn("{}/{} requires C++14. Your compiler is unknown. Assuming it supports C++14.".format(self.name, self.version))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["CATCH_INSTALL_DOCS"] = "OFF"
        cmake.definitions["CATCH_INSTALL_HELPERS"] = "ON"
        cmake.definitions["CATCH_CONFIG_PREFIX_ALL"] = self.options.with_prefix
        if self.options.default_reporter:
            cmake.definitions["CATCH_CONFIG_DEFAULT_REPORTER"] = self._default_reporter_str
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _patch_sources(self):
        for x in self.conan_data.get("patches", {}).get(self.version, []):
            patch(**x)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(os.path.join(self.package_folder, "share"))
        for cmake_file in ["ParseAndAddCatchTests.cmake", "Catch.cmake", "CatchAddTests.cmake"]:
            self.copy(
                cmake_file,
                src=os.path.join(self._source_subfolder, "extras"),
                dst=os.path.join("lib", "cmake", "Catch2"),
            )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Catch2")
        self.cpp_info.set_property("cmake_target_name", "Catch2::Catch2WithMain")
        self.cpp_info.set_property("pkg_config_name", "catch2-with-main")
        self.cpp_info.names["cmake_find_package"] = "Catch2"
        self.cpp_info.names["cmake_find_package_multi"] = "Catch2"

        lib_suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.components["_catch2"].set_property("cmake_target_name", "Catch2::Catch2")
        self.cpp_info.components["_catch2"].set_property("pkg_config_name", "catch2")
        self.cpp_info.components["_catch2"].names["cmake_find_package"] = "Catch2"
        self.cpp_info.components["_catch2"].names["cmake_find_package_multi"] = "Catch2"
        self.cpp_info.components["_catch2"].libs = ["Catch2" + lib_suffix]

        self.cpp_info.components["catch2_with_main"].builddirs = [os.path.join("lib", "cmake", "Catch2")]
        self.cpp_info.components["catch2_with_main"].libs = ["Catch2Main" + lib_suffix]
        self.cpp_info.components["catch2_with_main"].requires = ["_catch2"]
        self.cpp_info.components["catch2_with_main"].system_libs = ["log"] if self.settings.os == "Android" else []
        self.cpp_info.components["catch2_with_main"].set_property("cmake_target_name", "Catch2::Catch2WithMain")
        self.cpp_info.components["catch2_with_main"].set_property("pkg_config_name", "catch2-with-main")
        self.cpp_info.components["catch2_with_main"].names["cmake_find_package"] = "Catch2WithMain"
        self.cpp_info.components["catch2_with_main"].names["cmake_find_package_multi"] = "Catch2WithMain"
        defines = self.cpp_info.components["catch2_with_main"].defines

        if self.options.with_prefix:
            defines.append("CATCH_CONFIG_PREFIX_ALL")
        if self.options.default_reporter:
            defines.append("CATCH_CONFIG_DEFAULT_REPORTER={}".format(self._default_reporter_str))
