from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc, MSBuild, MSBuildToolchain
import os


required_conan_version = ">=1.53.0"


class SimdConan(ConanFile):
    name = "simd"
    description = "C++ image processing and machine learning library with SIMD"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ermig1979/Simd"
    topics = ("sse", "avx", "avx-512", "amx", "vmx", "vsx", "neon")
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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
        else:
            tc = CMakeToolchain(self)
            tc.variables["SIMD_AVX512"] = self.options.with_avx512
            tc.variables["SIMD_AVX512VNNI"] = self.options.with_avx512
            tc.variables["SIMD_AVX512BF16"] = self.options.with_avx512
            tc.variables["SIMD_TEST"] = False
            tc.variables["SIMD_SHARED"] = self.options.shared
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
            tc.generate()

    def build(self):
        if is_msvc(self):
            msbuild = MSBuild(self)
            msbuild.build(os.path.join(self.source_folder, "prj", "vs2022", "Simd.vcxproj"))
        else:
            cmake = CMake(self)
            cmake.configure(build_script_folder=os.path.join(self.source_folder, "prj", "cmake"))
            cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if is_msvc(self):
            copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include", "Simd"), src=os.path.join(self.source_folder, "src", "Simd"), keep_path=True)
            copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.source_folder, keep_path=False)
            copy(self, pattern="*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.source_folder, keep_path=False)
        else:
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
