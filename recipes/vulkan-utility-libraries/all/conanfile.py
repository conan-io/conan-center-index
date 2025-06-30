from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
import os


required_conan_version = ">=2.0.9"


class VulkanUtilityLibraries(ConanFile):
    name = "vulkan-utility-libraries"
    description = "Code shared across various Vulkan repositories, for Vulkan SDK developers and users."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KhronosGroup/Vulkan-Utility-Libraries"
    topics = ("vulkan")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"vulkan-headers/{self.version}", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22.1]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        license_folder = os.path.join(self.package_folder, "licenses")
        copy(self, "LICENSE.md", self.source_folder, license_folder)
        copy(self, "LICENSES/*", self.source_folder, license_folder, keep_path=False)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "VulkanUtilityLibraries")
        for component in ["SafeStruct", "LayerSettings", "UtilityHeaders"]:
            self.cpp_info.components[component].set_property("cmake_target_name", f"Vulkan::{component}")
            self.cpp_info.components[component].requires = ["vulkan-headers::vulkanheaders"]
            if component != "UtilityHeaders":
                self.cpp_info.components[component].libs = [f"Vulkan{component}"]
            else:
                self.cpp_info.components[component].libdirs = []
                self.cpp_info.components[component].bindirs = []
