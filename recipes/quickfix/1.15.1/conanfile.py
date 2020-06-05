from conans import ConanFile, CMake, tools
import shutil
import os
import re


class QuickfixConan(ConanFile):
    name = "quickfix"
    version = "1.15.1"
    license = "The QuickFIX Software License, Version 1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.quickfixengine.org"
    description = "QuickFIX is a free and open source implementation of the FIX protocol"
    topics = ("conan", "QuickFIX", "FIX", "Financial Information Exchange", "libraries", "cpp")
    settings = "os", "compiler", "build_type", "arch"
    options = {"ssl": [True, False], "fPIC": [True, False]}
    default_options = "ssl=False", "fPIC=True"
    generators = "cmake"
    file_pattern = re.compile(r'quickfix-(.*)')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

        files = os.listdir()
        quickfix_dir = list(filter(self.file_pattern.search, files))

        shutil.move(quickfix_dir[0], "quickfix")

        tools.replace_in_file("quickfix/CMakeLists.txt",
                              "project(${quickfix_PROJECT_NAME} VERSION 0.1 LANGUAGES CXX C)",
                              '''project(${quickfix_PROJECT_NAME} VERSION 0.1 LANGUAGES CXX C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

        tools.replace_in_file("quickfix/examples/executor/C++/CMakeLists.txt",
                              "add_executable(${executor_NAME} Application.cpp executor.cpp ${applink_SOURCE})",
                              "add_executable(${executor_NAME} Application.cpp executor.cpp)")

        tools.replace_in_file("quickfix/examples/tradeclient/CMakeLists.txt",
                              "add_executable(tradeclient Application.cpp tradeclient.cpp ${applink_SOURCE})",
                              "add_executable(tradeclient Application.cpp tradeclient.cpp)")

        tools.replace_in_file("quickfix/examples/ordermatch/CMakeLists.txt",
                              "add_executable(ordermatch Application.cpp Market.cpp ordermatch.cpp ${applink_SOURCE})",
                              "add_executable(ordermatch Application.cpp Market.cpp ordermatch.cpp)")

        os.makedirs("quickfix/include")
        shutil.copyfile("quickfix/src/C++/Except.h", "quickfix/include/Except.h")

    def requirements(self):
        if self.options.ssl:
            self.requires("openssl/[>=1.0.2a]")

    def configure(self):
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    def build(self):
        cmake = self._configure_cmake()
        cmake.build(target="quickfix")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("config.h", dst="include", src="quickfix")
        self.copy("Except.h", dst="include", src="quickfix/src/C++")
        self.copy("LICENSE", dst="licenses", src="quickfix")
        shutil.rmtree(f"{self.package_folder}{os.sep}share")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Windows":
            self.cpp_info.libs.append("ws2_32")
            self.cpp_info.libs.append("wsock32")

    def _configure_cmake(self):
        cmake = CMake(self)

        if self.options.ssl:
            cmake.definitions["HAVE_SSL"] = "ON"

        cmake.configure(source_folder="quickfix")
        return cmake
