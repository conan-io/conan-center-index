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
                              "cmake_minimum_required(VERSION 3.0 FATAL_ERROR)",
                              "cmake_minimum_required(VERSION 3.16 FATAL_ERROR)")

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

        tools.replace_in_file("quickfix/CMakeLists.txt",
                              "include(FindSharedPtr)",
                              '''message(STATUS "Checking for nullptr.")
unset(HAVE_NULLPTR CACHE)
set(NULLPTR_FOUND FALSE)
check_include_file_cxx(cstddef HAVE_STD_CSTDDEF_HEADER)
if (HAVE_STD_CSTDDEF_HEADER)
    include(CheckCXXSourceCompiles)
    check_cxx_source_compiles("#include <cstddef>
                               int main() {
                                 std::nullptr_t null = nullptr;
                                 return 0;
                               }"
            HAVE_NULLPTR)
    if (HAVE_NULLPTR)
        message(STATUS "Found support to nullptr.")
        set(NULLPTR_FOUND TRUE)
    endif(HAVE_NULLPTR)
endif(HAVE_STD_CSTDDEF_HEADER)

if (HAVE_NULLPTR)
    message(STATUS "set HAVE_NULLPTR")
    add_definitions("-DHAVE_NULLPTR=1")
    file(APPEND ${CMAKE_SOURCE_DIR}/config.h
     "#ifndef HAVE_NULLPTR\n"
     "#define HAVE_NULLPTR\n"
     "#endif\n" )
endif (HAVE_NULLPTR)

include(FindSharedPtr)
''')

        tools.replace_in_file("quickfix/CMakeLists.txt",
                              "include(FindSharedPtr)",
                              '''message(STATUS "Checking for use of enumeration in nested specifier.")
unset(HAVE_ENUM_NESTED CACHE)
set(ENUM_NESTED_FOUND FALSE)
check_cxx_source_compiles("namespace NS {
                           enum E {
                           Item
                           };
                           }
                           int main() {
                             NS::E e = NS::E::Item;
                           }"
                          HAVE_ENUM_NESTED)
if (HAVE_ENUM_NESTED)
    message(STATUS "Found support to use of enumeration in nested specifier.")
    set(ENUM_NESTED_FOUND TRUE)

    message(STATUS "set HAVE_ENUM_NESTED")
    add_definitions("-DHAVE_ENUM_NESTED=1")

    file(APPEND ${CMAKE_SOURCE_DIR}/config.h
     "#ifndef HAVE_ENUM_NESTED\n"
     "#define HAVE_ENUM_NESTED\n"
     "#endif\n" )
endif (HAVE_ENUM_NESTED)

include(FindSharedPtr)
''')

        tools.replace_in_file("quickfix/CMakeLists.txt",
                              "include(FindSharedPtr)",
                              '''message(STATUS "Checking support in-class initialization of non-static data member.")
unset(HAVE_IN_CLASS_NON_STATIC CACHE)
set(IN_CLASS_NON_STATIC_FOUND FALSE)
check_cxx_source_compiles("namespace NS {
                           class C {
                           int f = 0;
                           };
                           }
                           int main() {
                             NS::C c;
                           }"
                          HAVE_IN_CLASS_NON_STATIC)
if (HAVE_IN_CLASS_NON_STATIC)
    message(STATUS "Found support to in-class initialization of non-static data member.")
    set(IN_CLASS_NON_STATIC_FOUND TRUE)

    message(STATUS "set HAVE_IN_CLASS_NON_STATIC")
    add_definitions("-DHAVE_IN_CLASS_NON_STATIC=1")

    file(APPEND ${CMAKE_SOURCE_DIR}/config.h
     "#ifndef HAVE_IN_CLASS_NON_STATIC\n"
     "#define HAVE_IN_CLASS_NON_STATIC\n"
     "#endif\n" )
endif (HAVE_IN_CLASS_NON_STATIC)

include(FindSharedPtr)
''')

        tools.replace_in_file("quickfix/CMakeLists.txt",
                              'add_definitions("-DHAVE_STD_SHARED_PTR=1")',
                              '''
add_definitions("-DHAVE_STD_SHARED_PTR=1")
file(APPEND ${CMAKE_SOURCE_DIR}/config.h
 "#ifndef HAVE_STD_SHARED_PTR\n"
 "#define HAVE_STD_SHARED_PTR\n"
 "#endif\n" )
''')

        tools.replace_in_file("quickfix/CMakeLists.txt",
                              'add_definitions("-DHAVE_STD_TR1_SHARED_PTR=1")',
                              '''
add_definitions("-DHAVE_STD_TR1_SHARED_PTR=1")
file(APPEND ${CMAKE_SOURCE_DIR}/config.h
 "#ifndef HAVE_STD_TR1_SHARED_PTR\n"
 "#define HAVE_STD_TR1_SHARED_PTR\n"
 "#endif\n" )
''')

        tools.replace_in_file("quickfix/CMakeLists.txt",
                              'add_definitions("-DHAVE_STD_TR1_SHARED_PTR_FROM_TR1_MEMORY_HEADER=1")',
                              '''
add_definitions("-DHAVE_STD_TR1_SHARED_PTR_FROM_TR1_MEMORY_HEADER=1")
file(APPEND ${CMAKE_SOURCE_DIR}/config.h
 "#ifndef HAVE_STD_TR1_SHARED_PTR_FROM_TR1_MEMORY_HEADER\n"
 "#define HAVE_STD_TR1_SHARED_PTR_FROM_TR1_MEMORY_HEADER\n"
 "#endif\n" )
''')

        tools.replace_in_file("quickfix/CMakeLists.txt",
                              'add_definitions("-DHAVE_STD_UNIQUE_PTR=1")',
                              '''
add_definitions("-DHAVE_STD_UNIQUE_PTR=1")
file(APPEND ${CMAKE_SOURCE_DIR}/config.h
 "#ifndef HAVE_STD_UNIQUE_PTR\n"
 "#define HAVE_STD_UNIQUE_PTR\n"
 "#endif\n" )
''')

        tools.replace_in_file("quickfix/src/CMakeLists.txt",
                              "add_executable(ut ut.cpp getopt.c ${ut_SOURCES})",
                              '''
if ( NULLPTR_FOUND AND ENUM_NESTED_FOUND AND IN_CLASS_NON_STATIC_FOUND )
add_executable(ut ut.cpp getopt.c ${ut_SOURCES})
''')

        tools.replace_in_file("quickfix/src/CMakeLists.txt",
                              "add_executable(pt pt.cpp getopt.c)",
                              '''
endif ( NULLPTR_FOUND AND ENUM_NESTED_FOUND AND IN_CLASS_NON_STATIC_FOUND )
add_executable(pt pt.cpp getopt.c)
''')

        tools.replace_in_file("quickfix/src/C++/Utility.h",
                              "#elif defined(HAVE_STD_TR1_SHARED_PTR)",
                              "#elif defined(HAVE_STD_TR1_SHARED_PTR_FROM_TR1_MEMORY_HEADER)")

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
