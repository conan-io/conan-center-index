import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class DimeConan(ConanFile):
    name = "dime"
    description = "DXF (Data eXchange Format) file format support library."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin3d/dime"
    topics = ("dxf", "coin3d", "opengl", "graphics")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fixbig": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "fixbig": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DIME_BUILD_SHARED_LIBS"] = self.options.shared
        if self.options.fixbig:
            tc.preprocessor_definitions["DIME_FIXBIG"] = ""
        # Remove register keyword for C++17
        tc.preprocessor_definitions["register"] = ""
        tc.generate()

    def _patch_sources(self):
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            ("configure_file(${CMAKE_SOURCE_DIR}/${PROJECT_NAME_LOWER}.pc.cmake.in"
             " ${CMAKE_BINARY_DIR}/${PROJECT_NAME_LOWER}.pc @ONLY)"),
            ("configure_file(${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_NAME_LOWER}.pc.cmake.in"
             " ${CMAKE_BINARY_DIR}/${PROJECT_NAME_LOWER}.pc @ONLY)")
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.settings.os == "Windows" and is_msvc(self):
            rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        libname = "dime"
        if self.settings.os == "Windows" and is_msvc(self):
            libname = "{}{}{}{}".format(
                libname,
                Version(self.version).major,
                "" if self.options.shared else "s",
                "d" if self.settings.build_type == "Debug" else "",
            )
        self.cpp_info.libs = [libname]

        if self.settings.os == "Windows":
            self.cpp_info.defines.append("DIME_DLL" if self.options.shared else "DIME_NOT_DLL")
        if self.options.fixbig:
            self.cpp_info.defines.append("DIME_FIXBIG")

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)
