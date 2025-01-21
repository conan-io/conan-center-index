import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.scm import Version


required_conan_version = ">=1.53.0"


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

    @property
    def _min_cppstd(self):
        return "11"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8"
        }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "cmake/*", dst=self.export_sources_folder, src=self.recipe_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.get_safe("compiler.version")) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires {str(self.settings.compiler)}>={minimum_version}."
            )

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
        tc.variables["LLAMA_STANDALONE"] = False
        tc.variables["LLAMA_BUILD_TESTS"] = False
        tc.variables["LLAMA_BUILD_EXAMPLES"] = self.options.get_safe("with_examples")
        tc.variables["LLAMA_CURL"] = self.options.get_safe("with_curl")
        tc.variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.variables["GGML_CUDA"] = self.options.get_safe("with_cuda")
        if hasattr(self, "settings_build") and cross_building(self):
            tc.variables["LLAMA_NATIVE"] = False
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

    def package_info(self):
        self.cpp_info.components["common"].includedirs = [os.path.join("include", "common")]
        self.cpp_info.components["common"].libs = ["common"]
        self.cpp_info.components["common"].libdirs = ["lib"]
        if self.version >= Version("b3240"):
            self.cpp_info.components["common"].libs.append("ggml")

        self.cpp_info.components["llama"].libs = ["llama"]
        self.cpp_info.components["llama"].resdirs = ["res"]
        self.cpp_info.components["llama"].libdirs = ["lib"]

        if self.options.with_cuda and not self.options.shared:
            self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
            module_path = os.path.join("lib", "cmake", "llama-cpp-cuda-static.cmake")
            self.cpp_info.set_property("cmake_build_modules", [module_path])

        if is_apple_os(self):
            self.cpp_info.components["common"].frameworks.extend(["Foundation", "Accelerate", "Metal"])
        elif self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["common"].system_libs.extend(["dl", "m", "pthread", "gomp"])
