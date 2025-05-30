from conan import ConanFile, Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import cmake_layout, CMakeDeps, CMakeToolchain, CMake
from conan.tools.files import copy, get
import os

required_conan_version = ">=2"


class VulkanHppConan(ConanFile):
    name = "vulkan-hpp"
    description = "Open-Source Vulkan C++ API"
    license = "Apache-2.0"
    topics = ("vulkan-hpp", "vulkan", "gpu")
    homepage = "https://github.com/KhronosGroup/Vulkan-Headers"
    url = "https://github.com/KhronosGroup/Vulkan-Hpp/"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    options = {
        "precompile": [True, False],
        "run_generator": [True, False],
        "build_with_local_vulkan_hpp": [True, False],
        "enable_cpp20_modules": [True, False],
        "enable_std_module": [True, False],
        "disable_enhanced_mode": [True, False],
        "dispatch_loader_dynamic": [True, False],
        "flags_mask_type_as_public": [True, False],
        "handles_move_exchange": [True, False],
        "no_constructors": [True, False],
        "no_exceptions": [True, False],
        "no_nodiscard_warnings": [True, False],
        "no_setters": [True, False],
        "no_smart_handle": [True, False],
        "no_spaceship_operator": [True, False],
        "no_to_string": [True, False],
        "no_win32_prototypes": [True, False],
        "raii_no_exceptions": [True, False],
        "smart_handle_implicit_cast": [True, False],
        "typesafe_conversion": [True, False],
        "use_reflect": [True, False],
        "install": [True, False]
    }
    default_options = {
        "precompile": True,
        "run_generator": False,
        "build_with_local_vulkan_hpp": True,
        "enable_cpp20_modules": False,
        "enable_std_module": False,
        "disable_enhanced_mode": False,
        "dispatch_loader_dynamic": False,
        "flags_mask_type_as_public": False,
        "handles_move_exchange": False,
        "no_constructors": False,
        "no_exceptions": False,
        "no_nodiscard_warnings": False,
        "no_setters": False,
        "no_smart_handle": False,
        "no_spaceship_operator": False,
        "no_to_string": False,
        "no_win32_prototypes": False,
        "raii_no_exceptions": False,
        "smart_handle_implicit_cast": False,
        "typesafe_conversion": False,
        "use_reflect": False,
        "install": False
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler == "msvc" and Version(self.settings.compiler.version) < "193":
            raise ConanInvalidConfiguration("Visual Studio 2022 (MSVC 1930 or newer) is required by qt >= 6.8.3")

        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "14":
            raise ConanInvalidConfiguration("apple-clang >= 14 is required by qt >= 6.8.3")

    def source(self):
        data = self.conan_data["sources"][self.version]
        get(self, **data["source"], strip_root=True)
        get(self, **data["glfw"], strip_root=True, destination="glfw")
        get(self, **data["glm"], strip_root=True, destination="glm")
        get(self, **data["glslang"], strip_root=True, destination="glslang")
        get(self, **data["tinyxml2"], strip_root=True, destination="tinyxml2")
        get(self, **data["vulkan-headers"], strip_root=True, destination="Vulkan-Headers")

    def generate(self):
        if self.options.enable_cpp20_modules:
            tc = CMakeToolchain(self, generator="Ninja")
        else:
            tc = CMakeToolchain(self)
        tc.variables["VULKAN_HPP_PRECOMPILE"] = self.options.precompile
        tc.variables["VULKAN_HPP_RUN_GENERATOR"] = self.options.run_generator
        tc.variables["VULKAN_HPP_BUILD_WITH_LOCAL_VULKAN_HPP"] = self.options.build_with_local_vulkan_hpp
        tc.variables["VULKAN_HPP_ENABLE_CPP20_MODULES"] = self.options.enable_cpp20_modules
        tc.variables["VULKAN_HPP_ENABLE_STD_MODULE"] = self.options.enable_std_module
        tc.variables["VULKAN_HPP_DISABLE_ENHANCED_MODE"] = self.options.disable_enhanced_mode
        tc.variables["VULKAN_HPP_DISPATCH_LOADER_DYNAMIC"] = self.options.dispatch_loader_dynamic
        tc.variables["VULKAN_HPP_FLAGS_MASK_TYPE_AS_PUBLIC"] = self.options.flags_mask_type_as_public
        tc.variables["VULKAN_HPP_HANDLES_MOVE_EXCHANGE"] = self.options.handles_move_exchange
        tc.variables["VULKAN_HPP_NO_CONSTRUCTORS"] = self.options.no_constructors
        tc.variables["VULKAN_HPP_NO_EXCEPTIONS"] = self.options.no_exceptions
        tc.variables["VULKAN_HPP_NO_NODISCARD_WARNINGS"] = self.options.no_nodiscard_warnings
        tc.variables["VULKAN_HPP_NO_SETTERS"] = self.options.no_setters
        tc.variables["VULKAN_HPP_NO_SMART_HANDLE"] = self.options.no_smart_handle
        tc.variables["VULKAN_HPP_NO_SPACESHIP_OPERATOR"] = self.options.no_spaceship_operator
        tc.variables["VULKAN_HPP_NO_TO_STRING"] = self.options.no_to_string
        tc.variables["VULKAN_HPP_NO_WIN32_PROTOTYPES"] = self.options.no_win32_prototypes
        tc.variables["VULKAN_HPP_RAII_NO_EXCEPTIONS"] = self.options.raii_no_exceptions
        tc.variables["VULKAN_HPP_SMART_HANDLE_IMPLICIT_CAST"] = self.options.smart_handle_implicit_cast
        tc.variables["VULKAN_HPP_TYPESAFE_CONVERSION"] = self.options.typesafe_conversion
        tc.variables["VULKAN_HPP_USE_REFLECT"] = self.options.use_reflect
        tc.variables["VULKAN_HPP_INSTALL"] = self.options.run_generator and self.options.install
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        bin_path = os.path.join(self.package_folder, "bin")
        copy(self, "VideoHppGenerator*", src=self.cpp.build.bindir, dst=bin_path)
        copy(self, "VulkanHppGenerator*", src=self.cpp.build.bindir, dst=bin_path)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.path.append(bin_path)

        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
