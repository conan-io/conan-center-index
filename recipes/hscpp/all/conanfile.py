import os
from pathlib import Path

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.0.9"


class HscppConan(ConanFile):
    name = "hscpp"
    description = "A library to hot-reload C++ at runtime"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jheruty/hscpp"
    topics = ("hot-reload", "hot-swapping", "live-coding", "gamedev", "header-only")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if not valid_min_cppstd(self, 17):
            self.requires("ghc-filesystem/1.5.14")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("util-linux-libuuid/2.39.2")

    def validate(self):
        check_min_cppstd(self, 11)

    def build_requirements(self):
        self.tool_requires("cmake/[^3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        rmdir(self, "lib")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "add_subdirectory(lib/filesystem-1.3.4)",
                        "find_package(ghc_filesystem REQUIRED CONFIG)")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["HSCPP_BUILD_EXAMPLES"] = False
        tc.variables["HSCPP_BUILD_TESTS"] = False
        if not valid_min_cppstd(self, 17):
            tc.variables["HSCPP_USE_GHC_FILESYSTEM"] = True
            tc.variables["CMAKE_CXX_STANDARD"] = 11
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("ghc-filesystem", "cmake_target_name", "ghc_filesystem")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=Path(self.source_folder).parent)
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.pdb", self.package_folder, recursive=True)

    @property
    def _public_defines(self):
        defines = []
        if self.settings.build_type == "Debug":
            defines.append("HSCPP_DEBUG")
        if self.settings.os == "Windows":
            defines.append("HSCPP_PLATFORM_WIN32")
            defines.append("_CRT_SECURE_NO_WARNINGS")
        elif is_apple_os(self):
            defines.append("HSCPP_PLATFORM_APPLE")
            defines.append("HSCPP_PLATFORM_UNIX")
        else:
            defines.append("HSCPP_PLATFORM_UNIX")
        if is_msvc(self):
            defines.append("HSCPP_COMPILER_MSVC")
        elif self.settings.os == "Windows" and self.settings.compiler == "clang":
            defines.append("HSCPP_COMPILER_CLANG_CL")
        elif self.settings.compiler in ["clang", "apple-clang"]:
            defines.append("HSCPP_COMPILER_CLANG")
            defines.append("HSCPP_COMPILER_GCC")
        elif self.settings.compiler == "gcc":
            defines.append("HSCPP_COMPILER_GCC")
        if valid_min_cppstd(self, 17):
            defines.append(f"HSCPP_CXX_STANDARD={self.settings.compiler.cppstd}")
        else:
            defines.append("HSCPP_CXX_STANDARD=11")
            defines.append("HSCPP_USE_GHC_FILESYSTEM")
        return defines

    def package_info(self):
        self.cpp_info.libs = ["hscpp", "hscpp-mem"]
        self.cpp_info.defines = self._public_defines

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")
        elif is_apple_os(self):
            self.cpp_info.frameworks.extend(["CoreServices"])
