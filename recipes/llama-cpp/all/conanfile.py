import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, apply_conandata_patches, export_conandata_patches
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
        return Version(self.version) >= "b4570"

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "cmake/*", dst=self.export_sources_folder, src=self.recipe_folder)

    def validate(self):
        check_min_cppstd(self, 17 if self._is_new_llama else 11)

    def validate_build(self):
        if Version(self.version) >= "b4570" and self.settings.compiler == "msvc" and "arm" in self.settings.arch:
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
        copy(self, "*.cmake", src=os.path.join(self.export_sources_folder, "cmake"), dst=os.path.join(self.package_folder, "lib", "cmake"))

    def _get_backends(self):
        results = ["cpu"]
        if is_apple_os(self):
            results.append("blas")
            results.append("metal")
        if self.options.with_cuda:
            results.append("cuda")
        return results

    def package_info(self):
        self.cpp_info.components["llama"].set_property("cmake_target_aliases", ["common"])
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

        self.cpp_info.components["llama"].set_property("cmake_target_aliases", ["llama"])
        self.cpp_info.components["llama"].libs = ["llama"]
        self.cpp_info.components["llama"].resdirs = ["res"]

        if self.options.with_cuda and not self.options.shared:
            self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
            module_path = os.path.join("lib", "cmake", "llama-cpp-cuda-static.cmake")
            self.cpp_info.set_property("cmake_build_modules", [module_path])

        # New structure in llama
        if self._is_new_llama:
            self.cpp_info.components["llama"].requires = ["ggml"]

            self.cpp_info.components["ggml-base"].libs = ["ggml-base"]
            self.cpp_info.components["ggml-base"].resdirs = ["res"]
            if self.settings.os in ("Linux", "FreeBSD"):
                self.cpp_info.components["ggml-base"].system_libs.extend(["dl", "m", "pthread"])

            self.cpp_info.components["ggml"].libs = ["ggml"]
            self.cpp_info.components["ggml"].resdirs = ["res"]
            self.cpp_info.components["ggml"].requires = ["ggml-base"]
            self.cpp_info.components["ggml"].set_property("cmake_target_name", "ggml::all")
            if self.settings.os in ("Linux", "FreeBSD"):
                self.cpp_info.components["ggml"].system_libs.append("dl")

            if self.options.shared:
                self.cpp_info.components["llama"].defines.append("LLAMA_SHARED")
                self.cpp_info.components["ggml-base"].defines.append("GGML_SHARED")
                self.cpp_info.components["ggml"].defines.append("GGML_SHARED")

            backends = self._get_backends()
            for backend in backends:
                self.cpp_info.components[f"ggml-{backend}"].libs = [f"ggml-{backend}"]
                self.cpp_info.components[f"ggml-{backend}"].resdirs = ["res"]
                if self.options.shared:
                    self.cpp_info.components[f"ggml-{backend}"].defines.append("GGML_BACKEND_SHARED")
                self.cpp_info.components["ggml"].defines.append(f"GGML_USE_{backend.upper()}")
                self.cpp_info.components["ggml"].requires.append(f"ggml-{backend}")

            if is_apple_os(self):
                if "blas" in backends:
                    self.cpp_info.components["ggml-blas"].frameworks.append("Accelerate")
                if "metal" in backends:
                    self.cpp_info.components["ggml-metal"].frameworks.extend(["Metal", "MetalKit", "Foundation", "CoreFoundation"])
            if "cuda" in backends:
                # TODO: Add CUDA information
                pass
        else:
            if self.version >= Version("b3240"):
                self.cpp_info.components["common"].libs.append("ggml")
