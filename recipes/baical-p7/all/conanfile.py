import os
from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.29.1"

class BaicalP7Conan(ConanFile):
    name = "baical-p7"
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://baical.net/p7.html"
    topics = ("p7", "baical", "logging", "telemetry")
    description = "Baical P7 client"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.os not in ["Linux", "Windows"]:
            raise ConanInvalidConfiguration("P7 only supports Windows and Linux at this time")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination= self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["P7_TESTS_BUILD"] = False
        self._cmake.definitions["P7_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["P7_EXAMPLES_BUILD"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "Headers"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.remove_files_by_mask(os.path.join(self.package_folder, "include"), "*.cmake")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "p7"
        self.cpp_info.names["cmake_find_package_multi"] = "p7"

        if self.options.shared:
            self.cpp_info.components["p7"].name = "p7-shared"
            self.cpp_info.components["p7"].libs = ["p7-shared"]
        else:
            self.cpp_info.components["p7"].name = "p7"
            self.cpp_info.components["p7"].libs = ["p7"]

        if self.settings.os == "Linux":
            self.cpp_info.components["p7"].system_libs .extend(["rt", "pthread"])
        if self.settings.os == "Windows":
            self.cpp_info.components["p7"].system_libs .append("Ws2_32")
