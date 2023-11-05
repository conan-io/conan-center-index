from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"


class SimdConan(ConanFile):
    name = "simd"
    description = "C++ image processing and machine learning library with using of SIMD"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ermig1979/Simd"
    topics = ("simd", "sse", "avx", "avx-512", "amx", "vmx", "vsx", "neon")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_avx512": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_avx512": False,
    }

    @property
    def _min_cppstd(self):
        return 11

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
            check_min_cppstd(self, self._min_cppstd)
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "10.0":
            raise ConanInvalidConfiguration(f"{self.ref} isn't compiled correctly with gcc < 10 ")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SIMD_AVX512"] = self.options.with_avx512
        tc.variables["SIMD_AVX512VNNI"] = self.options.with_avx512
        tc.variables["SIMD_AVX512BF16"] = self.options.with_avx512
        tc.variables["SIMD_TEST"] = False
        tc.variables["SIMD_SHARED"] = self.options.shared
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "prj", "cmake"))
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["Simd"]
        self.cpp_info.set_property("cmake_file_name", "Simd")
        self.cpp_info.set_property("cmake_target_name", "Simd::Simd")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("m")
