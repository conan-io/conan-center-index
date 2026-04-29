import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, save
from conan.tools.scm import Version

required_conan_version = ">=2.1"


class GgmlConan(ConanFile):
    name = "ggml"
    description = "Tensor library for machine learning"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ggml-org/ggml"
    topics = ("machine-learning", "tensor", "llm", "ai")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_blas": [True, False],
        "with_cuda": [True, False],
        "with_accelerate": [True, False],
        "with_metal": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_blas": False,
        "with_cuda": False,
        "with_accelerate": True,
        "with_metal": True,
    }

    implements = ["auto_shared_fpic"]

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "clang": "9",
            "apple-clang": "12",
            "Visual Studio": "16",
            "msvc": "192",
        }

    @property
    def _cuda_build_module(self):
        return textwrap.dedent("""\
            find_dependency(CUDAToolkit REQUIRED)
            if (WIN32)
                # As of CUDA 12.3.1, Windows does not offer a static cublas library
                target_link_libraries(ggml::ggml-cuda INTERFACE CUDA::cudart_static CUDA::cublas CUDA::cublasLt CUDA::cuda_driver)
            else ()
                target_link_libraries(ggml::ggml-cuda INTERFACE CUDA::cudart_static CUDA::cublas_static CUDA::cublasLt_static CUDA::cuda_driver)
            endif()
        """)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

        if not is_apple_os(self):
            self.options.rm_safe("with_accelerate")
            self.options.rm_safe("with_metal")
        else:
            self.options.rm_safe("with_cuda")

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        if self.options.with_blas and is_apple_os(self):
            self.options.with_accelerate = True

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.options.get_safe("with_cuda") and self.options.shared:
            raise ConanInvalidConfiguration("with_cuda=True is only supported for static builds.")

    def validate_build(self):
        if self.settings.compiler == "msvc" and "arm" in str(self.settings.arch):
            raise ConanInvalidConfiguration("ggml does not support ARM architecture on msvc, use clang instead.")

    def requirements(self):
        if self.options.with_blas and not is_apple_os(self):
            self.requires("openblas/0.3.30")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        if self.options.with_blas and not is_apple_os(self):
            deps.set_property("openblas", "cmake_file_name", "BLAS")
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["GGML_STANDALONE"] = False
        tc.variables["GGML_BUILD_TESTS"] = False
        tc.variables["GGML_BUILD_EXAMPLES"] = False
        tc.variables["GGML_CCACHE"] = False
        tc.variables["GGML_NATIVE"] = False
        tc.variables["GGML_NATIVE_DEFAULT"] = False
        tc.variables["GGML_OPENMP"] = False
        tc.variables["GGML_BLAS"] = bool(self.options.with_blas)
        tc.variables["GGML_CUDA"] = bool(self.options.get_safe("with_cuda", False))
        if str(self.settings.arch) in ("x86", "x86_64"):
            tc.variables["GGML_SSE42"] = False
            tc.variables["GGML_AVX"] = False
            tc.variables["GGML_AVX2"] = False
            tc.variables["GGML_BMI2"] = False
            tc.variables["GGML_AVX512"] = False
            tc.variables["GGML_AVX512_VBMI"] = False
            tc.variables["GGML_AVX512_VNNI"] = False
            tc.variables["GGML_AVX512_BF16"] = False
            if self.settings.compiler != "msvc":
                tc.variables["GGML_FMA"] = False
                tc.variables["GGML_F16C"] = False
                tc.variables["GGML_AMX_TILE"] = False
                tc.variables["GGML_AMX_INT8"] = False
                tc.variables["GGML_AMX_BF16"] = False
        if self.options.with_blas:
            tc.variables["GGML_BLAS_VENDOR"] = "Apple" if is_apple_os(self) else "OpenBLAS"
        if is_apple_os(self):
            tc.variables["GGML_ACCELERATE"] = bool(self.options.get_safe("with_accelerate", False))
            tc.variables["GGML_METAL"] = bool(self.options.get_safe("with_metal", False))
            tc.variables["GGML_METAL_EMBED_LIBRARY"] = bool(self.options.get_safe("with_metal", False))
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.options.get_safe("with_cuda"):
            module_path = os.path.join(self.package_folder, "lib", "cmake", "ggml-cuda-static.cmake")
            if not self.options.shared:
                save(self, module_path, self._cuda_build_module)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ggml")

        self.cpp_info.components["ggml-base"].set_property("cmake_target_name", "ggml::ggml-base")
        self.cpp_info.components["ggml-base"].libs = ["ggml-base"]
        if self.options.shared:
            self.cpp_info.components["ggml-base"].defines.append("GGML_SHARED")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["ggml-base"].system_libs.extend(["m", "pthread"])

        self.cpp_info.components["ggml-cpu"].set_property("cmake_target_name", "ggml::ggml-cpu")
        self.cpp_info.components["ggml-cpu"].libs = ["ggml-cpu"]
        self.cpp_info.components["ggml-cpu"].requires = ["ggml-base"]
        if self.options.shared:
            self.cpp_info.components["ggml-cpu"].defines.append("GGML_BACKEND_SHARED")
        if is_apple_os(self) and self.options.get_safe("with_accelerate"):
            self.cpp_info.components["ggml-cpu"].frameworks.append("Accelerate")

        self.cpp_info.components["ggml"].set_property("cmake_target_name", "ggml::ggml")
        self.cpp_info.components["ggml"].libs = ["ggml"]
        self.cpp_info.components["ggml"].requires = ["ggml-base", "ggml-cpu"]
        self.cpp_info.components["ggml"].defines.append("GGML_USE_CPU")
        if self.options.shared:
            self.cpp_info.components["ggml"].defines.append("GGML_SHARED")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["ggml"].system_libs.append("dl")

        if self.options.with_blas:
            self.cpp_info.components["ggml-blas"].set_property("cmake_target_name", "ggml::ggml-blas")
            self.cpp_info.components["ggml-blas"].libs = ["ggml-blas"]
            self.cpp_info.components["ggml-blas"].requires = ["ggml-base"]
            if self.options.shared:
                self.cpp_info.components["ggml-blas"].defines.append("GGML_BACKEND_SHARED")
            if is_apple_os(self):
                self.cpp_info.components["ggml-blas"].frameworks.append("Accelerate")
            else:
                self.cpp_info.components["ggml-blas"].requires.append("openblas::openblas")
            self.cpp_info.components["ggml"].requires.append("ggml-blas")
            self.cpp_info.components["ggml"].defines.append("GGML_USE_BLAS")

        if self.options.get_safe("with_cuda"):
            self.cpp_info.components["ggml-cuda"].set_property("cmake_target_name", "ggml::ggml-cuda")
            self.cpp_info.components["ggml-cuda"].libs = ["ggml-cuda"]
            self.cpp_info.components["ggml-cuda"].requires = ["ggml-base"]
            if self.options.shared:
                self.cpp_info.components["ggml-cuda"].defines.append("GGML_BACKEND_SHARED")
            self.cpp_info.components["ggml"].requires.append("ggml-cuda")
            self.cpp_info.components["ggml"].defines.append("GGML_USE_CUDA")
            if not self.options.shared:
                self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
                module_path = os.path.join("lib", "cmake", "ggml-cuda-static.cmake")
                self.cpp_info.set_property("cmake_build_modules", [module_path])

        if is_apple_os(self) and self.options.get_safe("with_metal"):
            self.cpp_info.components["ggml-metal"].set_property("cmake_target_name", "ggml::ggml-metal")
            self.cpp_info.components["ggml-metal"].libs = ["ggml-metal"]
            self.cpp_info.components["ggml-metal"].requires = ["ggml-base"]
            self.cpp_info.components["ggml-metal"].frameworks.extend(["Foundation", "Metal", "MetalKit"])
            if self.options.shared:
                self.cpp_info.components["ggml-metal"].defines.append("GGML_BACKEND_SHARED")
            self.cpp_info.components["ggml"].requires.append("ggml-metal")
            self.cpp_info.components["ggml"].defines.append("GGML_USE_METAL")
