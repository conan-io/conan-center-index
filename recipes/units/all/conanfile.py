from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class UnitsConan(ConanFile):
    name = "units"
    description = (
        "A compile-time, header-only, dimensional analysis and unit conversion "
        "library for C++ with no dependencies"
    )
    license = "MIT"
    topics = ("unit-conversion", "dimensional-analysis",
              "template-metaprogramming", "compile-time", "header-only",
              "no-dependencies")
    homepage = "https://github.com/nholthaus/units"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    exports_sources = "conan_units_natvis.cmake"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def build_requirements(self):
        if Version(self.version) >= "3.0":
            # C++23 support and the Visual Studio 2022 generator.
            self.tool_requires("cmake/[>=3.21 <4]")

    def validate(self):
        min_cppstd = "23" if Version(self.version) >= "3.0" else "14"
        check_min_cppstd(self, min_cppstd)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) >= "3.0":
            tc.variables["UNITS_BUILD_TESTS"] = False
            tc.variables["UNITS_BUILD_DOCS"] = False
            tc.variables["UNITS_BUILD_EXAMPLES"] = False
            tc.variables["UNITS_INSTALL"] = True
        else:
            tc.variables["BUILD_TESTS"] = False
            tc.variables["BUILD_DOCS"] = False
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"  # CMake 4 support
        tc.generate()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share", "units", "cmake"))
        if Version(self.version) >= "3.0":
            copy(self, "conan_units_natvis.cmake", src=self.export_sources_folder,
                 dst=os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "units")
        self.cpp_info.set_property("cmake_target_name", "units::units")
        if Version(self.version) >= "3.0":
            self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "conan_units_natvis.cmake")])
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
