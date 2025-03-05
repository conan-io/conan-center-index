import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import save, copy, get, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


class LlamaCppConan(ConanFile):
    name = "llama-cpp"
    description = "Inference of LLaMA model in pure C/C++"
    topics = ("llama", "llm", "ai")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ggerganov/llama.cpp"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_examples": [True, False],
        "with_cuda": [True, False],
        "with_curl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_examples": False,
        "with_cuda": False,
        "with_curl": False,
    }

    implements = ["auto_shared_fpic"]

    @property
    def _is_new_llama(self):
        # Structure of llama.cpp libraries was changed after b4079
        return Version(self.version) >= "b4570"

    @property
    def _cuda_build_module(self):
        # Adding this to the package info is necessary if we want consumers of llama to link correctly when
        # they activate the CUDA option. In the future, when we have a CUDA recipe this could be removed.
        cuda_target = "ggml-cuda" if self._is_new_llama else "ggml"
        return textwrap.dedent(f"""\
            find_dependency(CUDAToolkit REQUIRED)
            if (WIN32)
                # As of CUDA 12.3.1, Windows does not offer a static cublas library
                target_link_libraries({cuda_target} INTERFACE CUDA::cudart_static CUDA::cublas CUDA::cublasLt CUDA::cuda_driver)
            else ()
                target_link_libraries({cuda_target} INTERFACE CUDA::cudart_static CUDA::cublas_static CUDA::cublasLt_static CUDA::cuda_driver)
            endif()
        """)

    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        check_min_cppstd(self, 17 if self._is_new_llama else 11)

    def validate_build(self):
        if self._is_new_llama and self.settings.compiler == "msvc" and "arm" in self.settings.arch:
            raise ConanInvalidConfiguration("llama-cpp does not support ARM architecture on msvc, it recommends to use clang instead")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_curl:
            self.requires("libcurl/[>=7.78 <9]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["LLAMA_STANDALONE"] = False
        tc.variables["LLAMA_BUILD_TESTS"] = False
        tc.variables["LLAMA_BUILD_EXAMPLES"] = self.options.get_safe("with_examples")
        tc.variables["LLAMA_CURL"] = self.options.get_safe("with_curl")
        if cross_building(self):
            tc.variables["LLAMA_NATIVE"] = False
            tc.variables["GGML_NATIVE_DEFAULT"] = False

        tc.variables["GGML_BUILD_TESTS"] = False
        # Follow with_examples when newer versions can compile examples,
        # right now it tries to add_subdirectory to a non-existent folder
        tc.variables["GGML_BUILD_EXAMPLES"] = False
        tc.variables["GGML_CUDA"] = self.options.get_safe("with_cuda")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        copy(self, "*", os.path.join(self.source_folder, "models"), os.path.join(self.package_folder, "res", "models"))
        copy(self, "*.h*", os.path.join(self.source_folder, "common"), os.path.join(self.package_folder, "include", "common"))
        copy(self, "*common*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*common*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, "*common*.so", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*common*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*common*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        if self.options.with_cuda and not self.options.shared:
            save(self, os.path.join(self.package_folder, "lib", "cmake", "llama-cpp-cuda-static.cmake"), self._cuda_build_module)

    def _get_backends(self):
        results = ["cpu"]
        if is_apple_os(self):
            results.append("blas")
            results.append("metal")
        if self.options.with_cuda:
            results.append("cuda")
        return results

    def package_info(self):
        self.cpp_info.components["ggml"].libs = ["ggml"]
        self.cpp_info.components["ggml"].resdirs = ["res"]
        self.cpp_info.components["ggml"].set_property("cmake_target_name", "ggml::all")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["ggml"].system_libs.append("dl")

        self.cpp_info.components["llama"].libs = ["llama"]
        self.cpp_info.components["llama"].resdirs = ["res"]
        self.cpp_info.components["llama"].requires.append("ggml")

        self.cpp_info.components["common"].includedirs = [os.path.join("include", "common")]
        self.cpp_info.components["common"].libs = ["common"]
        self.cpp_info.components["common"].requires = ["llama"]

        if self.options.with_curl:
            self.cpp_info.components["common"].requires.append("libcurl::libcurl")
            self.cpp_info.components["common"].defines.append("LLAMA_USE_CURL")

        if is_apple_os(self):
            self.cpp_info.components["common"].frameworks.extend(["Foundation", "Accelerate", "Metal"])
        elif self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["common"].system_libs.extend(["dl", "m", "pthread", "gomp"])

        if self.options.with_cuda and not self.options.shared:
            self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
            module_path = os.path.join("lib", "cmake", "llama-cpp-cuda-static.cmake")
            self.cpp_info.set_property("cmake_build_modules", [module_path])

        if self._is_new_llama:
            self.cpp_info.components["ggml-base"].libs = ["ggml-base"]
            self.cpp_info.components["ggml-base"].resdirs = ["res"]
            self.cpp_info.components["ggml-base"].set_property("cmake_target_name", "ggml-base")

            self.cpp_info.components["ggml"].requires = ["ggml-base"]
            if self.settings.os in ("Linux", "FreeBSD"):
                self.cpp_info.components["ggml-base"].system_libs.extend(["dl", "m", "pthread"])


            if self.options.shared:
                self.cpp_info.components["llama"].defines.append("LLAMA_SHARED")
                self.cpp_info.components["ggml-base"].defines.append("GGML_SHARED")
                self.cpp_info.components["ggml"].defines.append("GGML_SHARED")

            backends = self._get_backends()
            for backend in backends:
                self.cpp_info.components[f"ggml-{backend}"].libs = [f"ggml-{backend}"]
                self.cpp_info.components[f"ggml-{backend}"].resdirs = ["res"]
                self.cpp_info.components[f"ggml-{backend}"].set_property("cmake_target_name", f"ggml-{backend}")
                if self.options.shared:
                    self.cpp_info.components[f"ggml-{backend}"].defines.append("GGML_BACKEND_SHARED")
                self.cpp_info.components["ggml"].defines.append(f"GGML_USE_{backend.upper()}")
                self.cpp_info.components["ggml"].requires.append(f"ggml-{backend}")

            if is_apple_os(self):
                if "blas" in backends:
                    self.cpp_info.components["ggml-blas"].frameworks.append("Accelerate")
                if "metal" in backends:
                    self.cpp_info.components["ggml-metal"].frameworks.extend(["Metal", "MetalKit", "Foundation", "CoreFoundation"])
