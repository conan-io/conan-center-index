from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=1.52.0"

class ErkirConan(ConanFile):
    name = "erkir"
    description = "a C++ library for geodetic and trigonometric calculations"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/vahancho/erkir"
    topics = ("earth", "geodesy", "geography", "coordinate-systems", "geodetic", "datum")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _minimum_cpp_standard(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CODE_COVERAGE"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if Version(self.version) < "2.0.0":
            copy(self, pattern="*", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
            copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
            copy(self, pattern="*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder, keep_path=False)
            copy(self, pattern="*.dylib*", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
            copy(self, pattern="*.so", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
            copy(self, pattern="*.a", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        postfix = "d" if Version(self.version) >= "2.0.0" and self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"erkir{postfix}"]
