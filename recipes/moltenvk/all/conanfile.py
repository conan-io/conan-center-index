from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os

required_conan_version = ">=2"


class MoltenVKConan(ConanFile):
    name = "moltenvk"
    description = "MoltenVK is a Vulkan Portability implementation. It " \
                  "layers a subset of the high-performance, industry-standard " \
                  "Vulkan graphics and compute API over Apple's Metal " \
                  "graphics framework, enabling Vulkan applications to run " \
                  "on iOS and macOS."
    license = "Apache-2.0"
    topics = ("moltenvk", "khronos", "vulkan", "metal")
    homepage = "https://github.com/KhronosGroup/MoltenVK"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "tools": True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cereal/1.3.2")
        version = "1.4.350.0"
        self.requires("glslang", version)
        self.requires("spirv-cross", version)
        self.requires("vulkan-headers", version, transitive_headers=True)
        self.requires("spirv-tools", version)

    def validate(self):
        check_min_cppstd(self, 17)
        if self.settings.os not in ["Macos", "iOS", "tvOS"]:
            raise ConanInvalidConfiguration("Only supported on MacOS, iOS and tvOS")
        spirv_cross = self.dependencies["spirv-cross"]
        if spirv_cross.options.shared or not (spirv_cross.options.msl and spirv_cross.options.reflect):
            raise ConanInvalidConfiguration("Requires spirv-cross static with msl & reflect enabled")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MVK_BUILD_SHADER_CONVERTER_TOOL"] = self.options.tools
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["MoltenVK"]
        self.cpp_info.frameworks = ["Metal", "Foundation", "CoreFoundation", "QuartzCore", "IOSurface", "CoreGraphics"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["AppKit", "IOKit"])
        elif self.settings.os in ["iOS", "tvOS"]:
            self.cpp_info.frameworks.append("UIKit")

        self.cpp_info.requires = [
            "cereal::cereal", "glslang::glslang-core", "glslang::spirv", "spirv-cross::spirv-cross-core",
            "spirv-cross::spirv-cross-msl", "spirv-cross::spirv-cross-reflect", "vulkan-headers::vulkan-headers",
        ]
        self.cpp_info.requires.append("spirv-tools::spirv-tools-core")

        moltenvk_icd_path = os.path.join(self.package_folder, "lib", "MoltenVK_icd.json")
        self.runenv_info.prepend_path("VK_DRIVER_FILES", moltenvk_icd_path)
        self.runenv_info.prepend_path("VK_ICD_FILENAMES", moltenvk_icd_path)
