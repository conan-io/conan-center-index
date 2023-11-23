import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.55.0"


class VulkanUtilityLibrariesConan(ConanFile):
    name = "vulkan-utility-libraries"
    description = "Utility libraries for Vulkan developers"
    license = "Apache-2.0"
    topics = ("vulkan",)
    homepage = "https://github.com/KhronosGroup/Vulkan-ValidationLayers"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "9",
            "clang": "7",
            "gcc": "8",
            "msvc": "191",
            "Visual Studio": "15.7",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"vulkan-headers/{self.version}", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            return all(int(p1) < int(p2) for p1, p2 in zip(v1.split("."), v2.split(".")))

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.17.2 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        fix_apple_shared_install_name(self)

    @property
    def _exported_cxxflags(self):
        # https://github.com/KhronosGroup/Vulkan-Utility-Libraries/blob/vulkan-sdk-1.3.268.0/src/CMakeLists.txt#L9-L40
        cxxflags = []
        if self.settings.compiler in ["gcc", "clang", "apple-clang"]:
            cxxflags += [
                "-Wpedantic",
                "-Wunreachable-code",
                "-Wunused-function",
                "-Wall",
                "-Wextra",
                "-Wpointer-arith",
                "-Wextra-semi",
            ]
            if self.settings.compiler != "gcc":
                cxxflags += [
                    "-Wunreachable-code-return",
                    "-Wconversion",
                    "-Wimplicit-fallthrough",
                    "-Wstring-conversion",
                ]
        elif is_msvc(self):
            cxxflags += [
                "/W4",
                "/we5038",
                "/permissive-",
                "/MP",
            ]
        return cxxflags

    @property
    def _exported_defines(self):
        # https://github.com/KhronosGroup/Vulkan-Utility-Libraries/blob/vulkan-sdk-1.3.268.0/src/CMakeLists.txt#L42-L56
        defines = ["VK_ENABLE_BETA_EXTENSIONS"]
        if self.settings.os == "Windows":
            defines += [
                "NOMINMAX",
                "WIN32_LEAN_AND_MEAN",
                "VK_USE_PLATFORM_WIN32_KHR",
            ]
        elif self.settings.os == "Android":
            defines.append("VK_USE_PLATFORM_ANDROID_KHR")
        elif is_apple_os(self):
            defines.append("VK_USE_PLATFORM_METAL_EXT")
            if self.settings.os == "iOS":
                defines.append("VK_USE_PLATFORM_IOS_MVK")
            else:
                defines.append("VK_USE_PLATFORM_MACOS_MVK")
        return defines

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "VulkanUtilityLibraries")

        # Vulkan::UtilityHeaders
        self.cpp_info.components["VulkanUtilityHeaders"].set_property("cmake_target_name", "Vulkan::UtilityHeaders")
        self.cpp_info.components["VulkanUtilityHeaders"].requires = ["vulkan-headers::vulkanheaders"]
        self.cpp_info.components["VulkanUtilityHeaders"].libdirs = []
        self.cpp_info.components["VulkanUtilityHeaders"].bindirs = []

        # Vulkan::LayerSettings
        self.cpp_info.components["VulkanLayerSettings"].set_property("cmake_target_name", "Vulkan::LayerSettings")
        self.cpp_info.components["VulkanLayerSettings"].requires = ["vulkan-headers::vulkanheaders", "VulkanUtilityHeaders"]
        self.cpp_info.components["VulkanLayerSettings"].libs = ["VulkanLayerSettings"]
        self.cpp_info.components["VulkanLayerSettings"].bindirs = []

        # Vulkan::CompilerConfiguration
        if Version(self.version) >= "1.3.265":
            self.cpp_info.components["VulkanCompilerConfiguration"] = self.cpp_info.components["VulkanCompilerConfiguration"]
            self.cpp_info.components["VulkanCompilerConfiguration"].set_property("cmake_target_name", "Vulkan::CompilerConfiguration")
            self.cpp_info.components["VulkanCompilerConfiguration"].requires = ["vulkan-headers::vulkanheaders"]
            self.cpp_info.components["VulkanCompilerConfiguration"].cxxflags = self._exported_cxxflags
            self.cpp_info.components["VulkanCompilerConfiguration"].defines = self._exported_defines
            self.cpp_info.components["VulkanCompilerConfiguration"].includedirs = []
            self.cpp_info.components["VulkanCompilerConfiguration"].libdirs = []
            self.cpp_info.components["VulkanCompilerConfiguration"].bindirs = []
            self.cpp_info.components["VulkanLayerSettings"].requires.append("VulkanCompilerConfiguration")
