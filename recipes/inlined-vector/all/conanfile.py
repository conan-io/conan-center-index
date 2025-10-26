from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os


class InlinedVectorConan(ConanFile):
    name = "inlined-vector"
    version = "5.7.0"
    license = "MIT"
    author = "lloyal.ai <noreply@lloyal.ai>"
    url = "https://github.com/lloyal-ai/inlined-vector"
    homepage = "https://github.com/lloyal-ai/inlined-vector"
    description = ("A C++17/20 header-only vector-like container with Small Buffer "
                   "Optimization (SBO) and full allocator support. Zero external dependencies.")
    topics = ("header-only", "containers", "sbo", "vector", "cpp17", "cpp20", "allocator-aware")

    settings = "os", "compiler", "build_type", "arch"

    # Header-only package
    package_type = "header-library"
    no_copy_source = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["INLINED_VECTOR_BUILD_TESTS"] = False
        tc.variables["INLINED_VECTOR_BUILD_BENCHMARKS"] = False
        tc.variables["INLINED_VECTOR_BUILD_FUZZ_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "inlined-vector")
        self.cpp_info.set_property("cmake_target_name", "inlined-vector::inlined-vector")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # C++17 minimum
        self.cpp_info.set_property("cmake_target_compile_features", ["cxx_std_17"])
