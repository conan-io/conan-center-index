from conans import ConanFile, CMake, tools


class QuickfixConan(ConanFile):
    name = "quickfix"
    version = "1.15.1"
    license = "The QuickFIX Software License, Version 1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.quickfixengine.org"
    description = "QuickFIX is a free and open source implementation of the FIX protocol"
    topics = ("conan", "QuickFIX", "FIX", "Financial Information Exchange", "libraries", "cpp")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def source(self):
        self.run("git clone https://github.com/quickfix/quickfix.git")
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
        tools.replace_in_file("quickfix/CMakeLists.txt",
                              "project(${quickfix_PROJECT_NAME} VERSION 0.1 LANGUAGES CXX C)",
                              '''project(${quickfix_PROJECT_NAME} VERSION 0.1 LANGUAGES CXX C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = self._configure_cmake()
        cmake.build(target="quickfix")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("config.h", dst="include", src="quickfix")

    def package_info(self):
        self.cpp_info.libs = ["quickfix"]

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder="quickfix")
        return cmake
