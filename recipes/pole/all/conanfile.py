import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy

class poleRecipe(ConanFile):
    name = "pole"
    package_type = "library"

    # Optional metadata
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    description = "POLE is a portable C++ library to access structured storage."
    topics = ("compound file", "ole")
    # Conan V1 compat
    homepage = "https://github.com/otofoto/Pole"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):        
        tc = CMakeToolchain(self)       
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "pole/LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"),keep_path=False)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["pole"]
        