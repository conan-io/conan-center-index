# Conan recipe for Tiny Process Library
# This recipe packages the upstream project:
# https://gitlab.com/eidheim/tiny-process-library

import os

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import collect_libs, replace_in_file, get

class tinyProcessRecipe(ConanFile):
    name = "tiny-process-library"
    version = "2.0.4"

    # Optional metadata
    license = "MIT"
    url = "https://gitlab.com/eidheim/tiny-process-library"
    description = "A small platform independent library making it simple to create and stop new processes in C++, as well as writing to stdin and reading from stdout and stderr of a new process."
    topics = ("process")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = "patches/*", "conandata.yml"

    def source(self):
        src = self.conan_data["sources"][self.version]
        get(self, **src, strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        # Remove tests from package
        tc.variables["BUILD_TESTING"] = "OFF"
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared

        if self.options.get_safe("fPIC") is not None:
            tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
            
        tc.generate()

    def build(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")

        # Newer versions of CMake have deprecated < 3.5, so update the minimum version
        replace_in_file(
            self, cmakelists,
            "cmake_minimum_required(VERSION 3.1)",
            "cmake_minimum_required(VERSION 3.5)"
        )

        # Windows .lib wasn't being generated with set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS) for shared builds, so use set_target_properties instead
        if self.settings.os == "Windows":
            replace_in_file(
                self, cmakelists,
                "set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)",
                "set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)\n"
                "  set_target_properties(tiny-process-library PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)"
            )

        # Remove examples from package as they assume static builds
        replace_in_file(self, cmakelists,
                    "add_executable(examples examples.cpp)",
                    "# disabled for Conan package: add_executable(examples examples.cpp)")
        replace_in_file(self, cmakelists,
                    "target_link_libraries(examples tiny-process-library)",
                    "# disabled for Conan package: target_link_libraries(examples tiny-process-library)")
        
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # Specify cmake package name
        self.cpp_info.set_property("cmake_file_name", "tiny-process-library")
        self.cpp_info.set_property("cmake_target_name", "tiny-process-library::tiny-process-library")

        self.cpp_info.libs = collect_libs(self)