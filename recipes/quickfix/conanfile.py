from conans import ConanFile, CMake, tools
import shutil
import os


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
        os.makedirs("quickfix/include")
        shutil.copyfile("quickfix/src/C++/Except.h", "quickfix/include/Except.h")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build(target="quickfix")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("config.h", dst="include", src="quickfix")
        self.copy("Except.h", dst="include", src="quickfix/src/C++")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Windows":
            self.cpp_info.libs.append("ws2_32")
            self.cpp_info.libs.append("wsock32")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder="quickfix")
        return cmake
