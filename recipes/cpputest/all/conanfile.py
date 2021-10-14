import os

from conans import ConanFile, CMake, tools

class CppUTestConan(ConanFile):
    name = "cpputest"
    description = \
"CppUTest is a C /C++ based unit xUnit test framework for unit testing and for test-driving your code." \
"It is written in C++ but is used in C and C++ projects and frequently" \
"used in embedded systems but it works for any C/C++ project."
    license = "BSD-3-Clause"
    topics = ("conan", "testing", "unit-testing")
    homepage = "https://cpputest.github.io"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_extensions": [True, False],
        "with_leak_detection": [True, False],
    }
    default_options = {
        "fPIC": True,
        "with_extensions": True,
        "with_leak_detection": True,
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["STD_C"] = "ON"
        self._cmake.definitions["STD_CPP"] = "ON"
        self._cmake.definitions["C++11"] = "ON"
        self._cmake.definitions["MEMORY_LEAK_DETECTION"] = self.options.with_leak_detection
        self._cmake.definitions["EXTENSIONS"] = self.options.with_extensions
        self._cmake.definitions["LONGLONG"] = "ON"
        self._cmake.definitions["COVERAGE"] = "OFF"
        self._cmake.definitions["TESTS"] = "OFF"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "CppUTest", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CppUTest"
        self.cpp_info.names["cmake_find_package_multi"] = "CppUTest"
        self.cpp_info.names["pkg_config"] = "cpputest"

        self.cpp_info.components["CppUTest"].names["cmake_find_package"] = "CppUTest"
        self.cpp_info.components["CppUTest"].names["cmake_find_package_multi"] = "CppUTest"
        self.cpp_info.components["CppUTest"].libs = ["CppUTest"]

        if self.options.with_extensions:
            self.cpp_info.components["CppUTestExt"].names["cmake_find_package"] = "CppUTestExt"
            self.cpp_info.components["CppUTestExt"].names["cmake_find_package_multi"] = "CppUTestExt"
            self.cpp_info.components["CppUTestExt"].libs = ["CppUTestExt"]
            self.cpp_info.components["CppUTestExt"].requires = ["CppUTest"]

        if self.settings.os == "Windows":
            self.cpp_info.components["CppUTest"].system_libs.extend(["winmm"])
        elif self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["CppUTest"].system_libs = ["pthread"]
