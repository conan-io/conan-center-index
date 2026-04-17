from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
import os


required_conan_version = ">=2.1"


class NNPACKConan(ConanFile):
    name = "nnpack"
    description = "NNPACK is an acceleration package for neural network computations"
    license = " BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Maratyszcza/NNPACK"
    topics = ("neural-networks", "deep-learning", "machine-learning", "ai", "simd", "fft")
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
    language = "C"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpuinfo/[>=cci.20231129]")
        self.requires("pthreadpool/cci.20231129", transitive_headers=True)
        self.requires("psimd/cci.20200517")
        self.requires("fxdiv/cci.20200417")
        self.requires("fp16/cci.20210320")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("NNPACK is not supported on Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["NNPACK_BUILD_TESTS"] = False
        tc.cache_variables["NNPACK_BACKEND"] = "psimd"
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("cpuinfo", "cmake_target_name", "cpuinfo")
        deps.set_property("pthreadpool", "cmake_target_name", "pthreadpool")
        deps.set_property("fxdiv", "cmake_target_name", "fxdiv")
        deps.set_property("psimd", "cmake_target_name", "psimd")
        deps.set_property("fp16", "cmake_target_name", "fp16")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["nnpack"]
        self.cpp_info.set_property("cmake_target_name", "nnpack")
        # Hardcoded definitions
        self.cpp_info.defines.extend(["NNP_INFERENCE_ONLY=0", "NNP_CONVOLUTION_ONLY=0"])
