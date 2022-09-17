from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get
from conan.tools.scm import Version
import functools
import os
import yaml

required_conan_version = ">=1.51.1"


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

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "hide_vulkan_symbols": [True, False],
        "with_spirv_tools": [True, False],
        "tools": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "hide_vulkan_symbols": False,
        "with_spirv_tools": True,
        "tools": True,
    }

    @property
    def _dependencies_filename(self):
        return f"dependencies-{self.version}.yml"

    @property
    @functools.lru_cache(1)
    def _dependencies_versions(self):
        dependencies_filepath = os.path.join(self.recipe_folder, "dependencies", self._dependencies_filename)
        if not os.path.isfile(dependencies_filepath):
            raise ConanException(f"Cannot find {dependencies_filepath}")
        cached_dependencies = yaml.safe_load(open(dependencies_filepath))
        return cached_dependencies

    @property
    def _min_cppstd(self):
        return 11 if Version(self.version) < "1.1.9" else 17

    @property
    def _has_hide_vulkan_symbols_option(self):
        return Version(self.version) >= "1.1.7"

    def export(self):
        copy(self, f"dependencies/{self._dependencies_filename}", self.recipe_folder, self.export_folder)

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if not self._has_hide_vulkan_symbols_option:
            del self.options.hide_vulkan_symbols

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        elif self._has_hide_vulkan_symbols_option:
            del self.options.hide_vulkan_symbols

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cereal/1.3.2")
        self.requires(self._require("glslang"))
        self.requires(self._require("spirv-cross"))
        self.requires(self._require("vulkan-headers"))
        if self.options.with_spirv_tools:
            self.requires(self._require("spirv-tools"))

    def _require(self, recipe_name):
        if recipe_name not in self._dependencies_versions:
            raise ConanException(f"{recipe_name} is missing in {self._dependencies_filename}")
        return f"{recipe_name}/{self._dependencies_versions[recipe_name]}"

    def package_id(self):
        # MoltenVK >=1.O.42 requires at least XCode 12.0 (11.4 actually) at build
        # time but can be consumed by older compiler versions if shared
        if Version(self.version) >= "1.0.42" and self.options.shared:
            if Version(self.settings.compiler.version) < "12.0":
                compatible_pkg = self.info.clone()
                compatible_pkg.settings.compiler.version = "12.0"
                self.compatible_packages.append(compatible_pkg)

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if self.info.settings.os not in ["Macos", "iOS", "tvOS"]:
            raise ConanInvalidConfiguration(f"{self.ref} only supported on MacOS, iOS and tvOS")
        if self.info.settings.compiler != "apple-clang":
            raise ConanInvalidConfiguration(f"{self.ref} requires apple-clang")
        if Version(self.version) >= "1.0.42" and not self.info.options.shared:
            if Version(self.info.settings.compiler.version) < "12.0":
                raise ConanInvalidConfiguration(f"{self.ref} static requires XCode 12.0 or higher at build & consume time")

    def validate_build(self):
        if Version(self.version) >= "1.0.42":
            if Version(self.settings.compiler.version) < "12.0":
                raise ConanInvalidConfiguration(f"{self.ref} requires XCode 12.0 or higher at build time")
        spirv_cross = self.dependencies["spirv-cross"]
        if spirv_cross.options.shared or not spirv_cross.options.msl or not spirv_cross.options.reflect:
            raise ConanInvalidConfiguration(f"{self.ref} requires spirv-cross static with msl & reflect enabled")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MVK_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["MVK_VERSION"] = self.version
        tc.variables["MVK_WITH_SPIRV_TOOLS"] = self.options.with_spirv_tools
        tc.variables["MVK_BUILD_SHADERCONVERTER_TOOL"] = self.options.tools
        if self._has_hide_vulkan_symbols_option and self.options.shared:
            tc.variables["MVK_HIDE_VULKAN_SYMBOLS"] = self.options.hide_vulkan_symbols
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
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

        if self.options.shared:
            moltenvk_icd_path = os.path.join(self.package_folder, "lib", "MoltenVK_icd.json")
            self.output.info(f"Prepending to VK_ICD_FILENAMES runtime environment variable: {moltenvk_icd_path}")
            self.runenv_info.prepend_path("VK_ICD_FILENAMES", moltenvk_icd_path)
            # TODO: to remove after conan v2, it allows to not break consumers still relying on virtualenv generator
            self.env_info.VK_ICD_FILENAMES.append(moltenvk_icd_path)

        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.PATH.append(bin_path)
