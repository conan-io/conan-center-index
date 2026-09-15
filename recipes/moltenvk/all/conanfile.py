from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file
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
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cereal/1.3.2")
        version = "1.4.357.0"
        self.requires(f"glslang/{version}")
        self.requires(f"spirv-cross/{version}")
        self.requires(f"vulkan-headers/{version}", transitive_headers=True)
        self.requires(f"spirv-tools/{version}")

    def validate(self):
        check_min_cppstd(self, 17)
        if self.settings.os not in ["Macos", "iOS", "tvOS"]:
            raise ConanInvalidConfiguration("Only supported on MacOS, iOS and tvOS")
        spirv_cross = self.dependencies["spirv-cross"]
        if spirv_cross.options.shared or not (spirv_cross.options.msl and spirv_cross.options.reflect):
            raise ConanInvalidConfiguration("Requires spirv-cross static with msl & reflect enabled")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Let CMakeToolchain control the C++ standard instead of hardcoding it upstream
        replace_in_file(
            self, os.path.join(self.source_folder, "CMakeLists.txt"),
            "\tset(CMAKE_CXX_STANDARD 17)\n"
            "\tset(CMAKE_CXX_STANDARD_REQUIRED ON)\n"
            "\tset(CMAKE_CXX_EXTENSIONS OFF)\n",
            "",
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MVK_BUILD_SHADER_CONVERTER_TOOL"] = self.options.tools
        tc.generate()
        deps = CMakeDeps(self)
        # MoltenVK's cmake/recipes/*.cmake scripts guard their CPM fallback behind
        # if(TARGET <name>) checks using the upstream project names, not Conan's
        # default lowercase package names. Align the global targets so find_package()
        # satisfies those guards instead of falling through to CPMAddPackage().
        deps.set_property("spirv-cross", "cmake_target_name", "SPRIV-Cross::SPRIV-Cross")
        deps.set_property("spirv-tools", "cmake_target_name", "SPIRV-Tools::SPIRV-Tools")
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
