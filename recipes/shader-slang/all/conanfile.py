import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, mkdir, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class ShaderSlangConan(ConanFile):
    name = "shader-slang"
    description = (
        "Slang is a shading language that makes it easier to build and maintain large shader"
        " codebases in a modular and extensible fashion, while also maintaining the highest possible"
        " performance on modern GPUs and graphics APIs."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/shader-slang/slang"
    topics = ("shaders", "vulkan", "glsl", "cuda", "hlsl", "d3d12")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_gfx": [True, False],
        "with_x11": [True, False],
        "with_cuda": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_gfx": False,
        "with_x11": True,
        "with_cuda": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "8",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.enable_gfx or self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_x11

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glslang/1.3.290.0")
        self.requires("spirv-headers/1.3.290.0")
        self.requires("spirv-tools/1.3.290.0")
        self.requires("lz4/1.10.0")
        self.requires("miniz/3.0.2")
        self.requires("unordered_dense/4.4.0")
        if self.options.enable_gfx:
            self.requires("vulkan-headers/1.3.290.0")
            self.requires("imgui/1.91.0")
            if is_apple_os(self):
                self.requires("metal-cpp/14.2")
            if self.options.get_safe("with_x11"):
                self.requires("xorg/system")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.25 <4]")
        if not can_run(self):
            self.tool_requires(f"shader-slang/{self.version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SLANG_LIB_TYPE"] = "SHARED" if self.options.shared else "STATIC"
        tc.cache_variables["SLANG_ENABLE_PREBUILT_BINARIES"] = False
        tc.cache_variables["SLANG_ENABLE_TESTS"] = False
        tc.cache_variables["SLANG_ENABLE_EXAMPLES"] = False
        tc.cache_variables["SLANG_ENABLE_GFX"] = self.options.enable_gfx
        tc.cache_variables["SLANG_ENABLE_XLIB"] = self.options.get_safe("with_x11", False)
        tc.cache_variables["SLANG_ENABLE_CUDA"] = self.options.get_safe("with_cuda", False)
        tc.cache_variables["SLANG_SLANG_LLVM_FLAVOR"] = "USE_SYSTEM_LLVM" if self.options.get_safe("with_llvm") else "DISABLE"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        VirtualBuildEnv(self).generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Everything except dxc/dxcapi.h is unvendored
        mkdir(self, os.path.join(self.source_folder, "external_headers"))
        os.rename(os.path.join(self.source_folder, "external", "dxc"),
                  os.path.join(self.source_folder, "external_headers", "dxc"))
        rmdir(self, os.path.join(self.source_folder, "external"))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if self.settings_target is not None:
            # Build and install native build tools for cross-compilation
            cmake.build(target="generators")
            cmake.build(target="slang-bootstrap")

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if self.settings_target is not None:
            cmake.install(component="generators")
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["slang_"].libs = ["slang"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["slang_"].system_libs.extend(["m", "pthread", "dl", "rt"])
        self.cpp_info.components["slang_"].requires = [
            "miniz::miniz",
            "lz4::lz4",
            "glslang::glslang-core",
            "glslang::spirv",
            "spirv-tools::spirv-tools-opt",
            "spirv-headers::spirv-headers",
            "unordered_dense::unordered_dense"
        ]

        self.cpp_info.components["slang-glslang"].libs = ["slang-glslang"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["slang-glslang"].system_libs.extend(["m", "pthread", "rt"])
        self.cpp_info.components["slang-glslang"].requires = [
            "glslang::glslang-core",
            "glslang::spirv",
            "spirv-tools::spirv-tools-opt",
            "spirv-headers::spirv-headers",
            "unordered_dense::unordered_dense"
        ]

        self.cpp_info.components["slang-rt"].libs = ["slang-rt"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["slang-rt"].system_libs.extend(["m", "pthread", "dl"])
        self.cpp_info.components["slang-rt"].requires = ["miniz::miniz", "lz4::lz4"]

        if self.options.enable_gfx:
            self.cpp_info.components["gfx"].libs = ["gfx"]
            self.cpp_info.components["gfx"].requires = ["slang_", "vulkan-headers::vulkan-headers"]
            if is_apple_os(self):
                self.cpp_info.components["gfx"].requires.append("metal-cpp::metal-cpp")
            if self.options.get_safe("with_x11"):
                self.cpp_info.components["gfx"].requires.append("xorg::x11")
            if self.options.with_cuda:
                self.cpp_info.components["gfx"].system_libs.append("cuda")

        if self.options.enable_gfx:
            self.cpp_info.components["_tools"].requires = ["imgui::imgui"]
