from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import copy, get, save
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

import os
import textwrap


required_conan_version = ">=1.53.0"


class StdexecConan(ConanFile):
    name = "stdexec"
    description = "Reference implementation of C++26 std::execution"
    license = "Apache-2.0 WITH LLVM-exception"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NVIDIA/stdexec"
    topics = ("execution", "senders", "receivers", "concurrency", "header-only")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _minimum_compilers_version(self):
        return {
            "apple-clang": "16",
            "clang": "16",
            "gcc": "12",
            "msvc": "194",
            "Visual Studio": "17",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd} support. "
                f"The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = False
        if self.options.get_safe("fPIC") is not None:
            tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        tc.generate()

    def _write_version_header(self):
        major, minor = str(self.version).split(".")
        save(
            self,
            os.path.join(self.build_folder, "stdexec_version_config.hpp"),
            textwrap.dedent(f"""\
                #pragma once

                #define STDEXEC_VERSION "{self.version}"
                #define STDEXEC_VERSION_MAJOR {major}
                #define STDEXEC_VERSION_MINOR {int(minor)}
                #define STDEXEC_VERSION_PATCH 0
                """),
        )

    def _write_cmakelists(self):
        save(
            self,
            os.path.join(self.build_folder, "CMakeLists.txt"),
            textwrap.dedent("""\
                cmake_minimum_required(VERSION 3.15)
                project(conan_stdexec LANGUAGES CXX)

                include(GNUInstallDirs)
                find_package(Threads REQUIRED)

                add_library(system_context STATIC
                    "${STDEXEC_SOURCE_DIR}/src/system_context/system_context.cpp")
                add_library(STDEXEC::system_context ALIAS system_context)

                target_compile_features(system_context PUBLIC cxx_std_20)
                target_include_directories(system_context
                    PUBLIC
                        "${STDEXEC_SOURCE_DIR}/include"
                        "${CMAKE_CURRENT_BINARY_DIR}")
                target_link_libraries(system_context PUBLIC Threads::Threads)

                if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
                    target_compile_options(system_context PUBLIC
                        -fcoroutines
                        -fconcepts-diagnostics-depth=10)
                elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
                    target_compile_options(system_context PUBLIC
                        /Zc:__cplusplus
                        /Zc:preprocessor)
                endif()

                target_compile_definitions(system_context PUBLIC
                    STDEXEC_ENABLE_EXTRA_TYPE_CHECKING=0
                    STDEXEC_ENABLE_IO_URING=0
                    STDEXEC_ENABLE_NUMA=0
                    $<$<PLATFORM_ID:Darwin>:STDEXEC_ENABLE_LIBDISPATCH=1>
                    $<$<NOT:$<PLATFORM_ID:Darwin>>:STDEXEC_ENABLE_LIBDISPATCH=0>
                    $<$<PLATFORM_ID:Windows>:STDEXEC_ENABLE_WINDOWS_THREAD_POOL=1>
                    $<$<NOT:$<PLATFORM_ID:Windows>>:STDEXEC_ENABLE_WINDOWS_THREAD_POOL=0>)

                install(TARGETS system_context
                    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
                    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
                    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
                """),
        )

    def build(self):
        self._write_version_header()
        self._write_cmakelists()
        cmake = CMake(self)
        cmake.configure(
            variables={"STDEXEC_SOURCE_DIR": self.source_folder.replace("\\", "/")},
            build_script_folder=self.build_folder,
        )
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(
            self,
            pattern="*",
            src=os.path.join(self.source_folder, "include"),
            dst=os.path.join(self.package_folder, "include"),
            excludes=("._clangd_helper_file.cpp", "*.in", "*.md"),
        )
        copy(
            self,
            pattern="stdexec_version_config.hpp",
            src=self.build_folder,
            dst=os.path.join(self.package_folder, "include"),
        )

        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "STDEXEC")

        self.cpp_info.components["stdexec"].set_property("cmake_target_name", "STDEXEC::stdexec")
        self.cpp_info.components["stdexec"].libdirs = []
        self.cpp_info.components["stdexec"].bindirs = []
        self.cpp_info.components["stdexec"].defines = [
            "STDEXEC_ENABLE_EXTRA_TYPE_CHECKING=0",
            "STDEXEC_ENABLE_IO_URING=0",
            "STDEXEC_ENABLE_NUMA=0",
            f"STDEXEC_ENABLE_LIBDISPATCH={1 if self.settings.os == 'Macos' else 0}",
            f"STDEXEC_ENABLE_WINDOWS_THREAD_POOL={1 if self.settings.os == 'Windows' else 0}",
        ]

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["stdexec"].system_libs.append("pthread")

        compiler = str(self.settings.compiler)
        if compiler == "gcc":
            self.cpp_info.components["stdexec"].cxxflags.extend([
                "-fcoroutines",
                "-fconcepts-diagnostics-depth=10",
            ])
        elif compiler in ("msvc", "Visual Studio"):
            self.cpp_info.components["stdexec"].cxxflags.extend([
                "/Zc:__cplusplus",
                "/Zc:preprocessor",
            ])

        self.cpp_info.components["system_context"].set_property("cmake_target_name", "STDEXEC::system_context")
        self.cpp_info.components["system_context"].libs = ["system_context"]
        self.cpp_info.components["system_context"].requires = ["stdexec"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "STDEXEC"
        self.cpp_info.names["cmake_find_package_multi"] = "STDEXEC"
        self.cpp_info.components["stdexec"].names["cmake_find_package"] = "stdexec"
        self.cpp_info.components["stdexec"].names["cmake_find_package_multi"] = "stdexec"
        self.cpp_info.components["system_context"].names["cmake_find_package"] = "system_context"
        self.cpp_info.components["system_context"].names["cmake_find_package_multi"] = "system_context"
