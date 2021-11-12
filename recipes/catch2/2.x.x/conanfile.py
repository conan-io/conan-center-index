import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class ConanRecipe(ConanFile):
    name = "catch2"
    description = "A modern, C++-native, header-only, framework for unit-tests, TDD and BDD"
    topics = ("conan", "catch2", "header-only", "unit-test", "tdd", "bdd")
    homepage = "https://github.com/catchorg/Catch2"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "with_main": [True, False],
        "with_benchmark": [True, False],
        "with_prefix": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_main": False,
        "with_benchmark": False,
        "with_prefix": False,
    }
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if not self.options.with_main:
            del self.options.fPIC
            del self.options.with_benchmark

    def validate(self):
        if tools.Version(self.version) < "2.13.1" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("ARMv8 is supported by 2.13.1+ only! give up!")
        if self.options.with_main and tools.Version(self.version) < "2.13.4":
            raise ConanInvalidConfiguration("Option with_main not supported with versions < 2.13.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = "OFF"
        self._cmake.definitions["CATCH_INSTALL_DOCS"] = "OFF"
        self._cmake.definitions["CATCH_INSTALL_HELPERS"] = "ON"
        self._cmake.definitions["CATCH_BUILD_STATIC_LIBRARY"] = self.options.with_main
        self._cmake.definitions["enable_benchmark"] = self.options.get_safe("with_benchmark", False)
        self._cmake.definitions["CATCH_CONFIG_PREFIX_ALL"] = self.options.with_prefix

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        # Catch2 does skip install if included as subproject:
        # https://github.com/catchorg/Catch2/blob/79a5cd795c387e2da58c13e9dcbfd9ea7a2cfb30/CMakeLists.txt#L100-L102
        main_cml = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(main_cml, "if (NOT_SUBPROJECT)", "if (TRUE)")
        if self.options.with_main:
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        for cmake_file in ["ParseAndAddCatchTests.cmake", "Catch.cmake", "CatchAddTests.cmake"]:
            self.copy(
                cmake_file,
                src=os.path.join(self._source_subfolder, "contrib"),
                dst=os.path.join("lib", "cmake", "Catch2"),
            )

    def package_id(self):
        if not self.options.with_main:
            self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Catch2"
        self.cpp_info.names["cmake_find_package_multi"] = "Catch2"

        if self.options.with_main:
            self.cpp_info.components["Catch2"].names["cmake_find_package"] = "Catch2"
            self.cpp_info.components["Catch2"].names["cmake_find_package_multi"] = "Catch2"

            self.cpp_info.components["Catch2WithMain"].builddirs = [os.path.join("lib", "cmake", "Catch2")]
            self.cpp_info.components["Catch2WithMain"].libs = ["Catch2WithMain"]
            self.cpp_info.components["Catch2WithMain"].system_libs = ["log"] if self.settings.os == "Android" else []
            self.cpp_info.components["Catch2WithMain"].names["cmake_find_package"] = "Catch2WithMain"
            self.cpp_info.components["Catch2WithMain"].names["cmake_find_package_multi"] = "Catch2WithMain"
            if self.options.get_safe("with_benchmark", False):
                self.cpp_info.components["Catch2WithMain"].defines.append("CATCH_CONFIG_ENABLE_BENCHMARKING")
            if self.options.with_prefix:
                self.cpp_info.components["Catch2WithMain"].defines.append("CATCH_CONFIG_PREFIX_ALL")
        else:
            self.cpp_info.builddirs = [os.path.join("lib", "cmake", "Catch2")]
            self.cpp_info.system_libs = ["log"] if self.settings.os == "Android" else []
            if self.options.with_prefix:
                self.cpp_info.defines.append("CATCH_CONFIG_PREFIX_ALL")
