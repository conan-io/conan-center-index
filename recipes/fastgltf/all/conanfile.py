from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd

import os

required_conan_version = ">2.0"


class fastgltf(ConanFile):
    name = "fastgltf"
    description = "A modern C++17 glTF 2.0 library focused on speed, correctness, and usability"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/spnda/fastgltf"
    topics = ("gltf", "simd", "cpp17")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_small_vector": [True, False],
        "disable_custom_memory_pool": [True, False],
        "use_64bit_float": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_small_vector": False,
        "disable_custom_memory_pool": False,
        "use_64bit_float": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder='src')

    def requirements(self):
        self.requires("simdjson/3.11.5")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.enable_small_vector:
            tc.variables["FASTGLTF_USE_CUSTOM_SMALLVECTOR"] = True
        if self.options.get_safe("disable_custom_memory_pool"):
            tc.variables["FASTGLTF_DISABLE_CUSTOM_MEMORY_POOL"] = True
        if self.options.get_safe("use_64bit_float"):
            tc.variables["FASTGLTF_USE_64BIT_FLOAT"] = True

        tc.variables["FASTGLTF_COMPILE_AS_CPP20"] = "20" in str(self.settings.get_safe("compiler.cppstd"))
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["fastgltf"]
        if "20" in str(self.settings.get_safe("compiler.cppstd")):
            self.cpp_info.defines.append("FASTGLTF_CPP_20")
