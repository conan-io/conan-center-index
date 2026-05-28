from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.files import apply_conandata_patches, get, export_conandata_patches


required_conan_version = ">=2.1"


class EVEConan(ConanFile):
    name = "eve"
    description = "EVE is a C++20 and onward implementation of a type based wrapper around SIMD extensions sets for most current architectures."
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://jfalcou.github.io/eve/"
    topics = ("eve", "simd", "c++", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["EVE_BUILD_DOCUMENTATION"] = False
        tc.variables["EVE_BUILD_TEST"] = False
        tc.variables["EVE_BUILD_INTEGRATION"] = False
        tc.variables["EVE_BUILD_BENCHMARKS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        # License is installed into the doc folder by the cmake install routine.
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.includedirs = [f"include/eve-{self.version}"]
        self.cpp_info.set_property("cmake_file_name", "eve")
        self.cpp_info.set_property("cmake_target_name", "eve::eve")
        
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
