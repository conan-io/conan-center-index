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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"vulkan-headers/{self.version}", transitive_headers=True)

    def validate(self):
        if self.settings.compiler == "msvc" and Version(self.settings.compiler.version) < "193":
            raise ConanInvalidConfiguration("Visual Studio 2022 (MSVC 1930 or newer) is required by qt >= 6.8.3")

        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "14":
            raise ConanInvalidConfiguration("apple-clang >= 14 is required by qt >= 6.8.3")

    def source(self):
        data = self.conan_data["sources"][self.version]
        get(self, **data["source"], strip_root=True)
        get(self, **data["tinyxml2"], strip_root=True, destination="tinyxml2")

    def generate(self):
        tc = CMakeToolchain(self)
        #tc.variables["VULKAN_HPP_GENERATOR_BUILD"] = False
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
