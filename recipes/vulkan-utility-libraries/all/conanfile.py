import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.0"


class VulkanUtilityLibrariesConan(ConanFile):
    name = "vulkan-utility-libraries"
    description = "Utility libraries for Vulkan developers"
    license = "Apache-2.0"
    topics = ("vulkan",)
    homepage = "https://github.com/KhronosGroup/Vulkan-Utility-Libraries"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"vulkan-headers/{self.version}", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.17.2 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")

    def build(self):
        self._patch_sources()
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
        self.cpp_info.components["UtilityHeaders"].set_property("cmake_target_name", "Vulkan::UtilityHeaders")
        self.cpp_info.components["UtilityHeaders"].requires = ["vulkan-headers::vulkanheaders"]
        self.cpp_info.components["UtilityHeaders"].libdirs = []
        self.cpp_info.components["UtilityHeaders"].bindirs = []

        # Vulkan::LayerSettings
        self.cpp_info.components["LayerSettings"].set_property("cmake_target_name", "Vulkan::LayerSettings")
        self.cpp_info.components["LayerSettings"].requires = ["vulkan-headers::vulkanheaders", "UtilityHeaders"]
        self.cpp_info.components["LayerSettings"].libs = ["VulkanLayerSettings"]
        self.cpp_info.components["LayerSettings"].bindirs = []

        # Vulkan::CompilerConfiguration
        if Version(self.version) >= "1.3.265":
            self.cpp_info.components["CompilerConfiguration"].set_property("cmake_target_name", "Vulkan::CompilerConfiguration")
            self.cpp_info.components["CompilerConfiguration"].requires = ["vulkan-headers::vulkanheaders"]
            self.cpp_info.components["CompilerConfiguration"].cxxflags = self._exported_cxxflags
            self.cpp_info.components["CompilerConfiguration"].defines = self._exported_defines
            self.cpp_info.components["CompilerConfiguration"].includedirs = []
            self.cpp_info.components["CompilerConfiguration"].libdirs = []
            self.cpp_info.components["CompilerConfiguration"].bindirs = []
            self.cpp_info.components["LayerSettings"].requires.append("CompilerConfiguration")

        # Vulkan::SafeStruct
        if Version(self.version) >= "1.3.282":
            self.cpp_info.components["SafeStruct"].set_property("cmake_target_name", "Vulkan::SafeStruct")
            self.cpp_info.components["SafeStruct"].requires = ["vulkan-headers::vulkanheaders", "UtilityHeaders", "CompilerConfiguration"]
            self.cpp_info.components["SafeStruct"].libs = ["VulkanSafeStruct"]
            self.cpp_info.components["SafeStruct"].bindirs = []
            self.cpp_info.components["LayerSettings"].requires.append("SafeStruct")
