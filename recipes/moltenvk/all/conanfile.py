from conan import ConanFile, tools
from conans import CMake
from conans.errors import ConanException, ConanInvalidConfiguration
import functools
import os
import yaml

required_conan_version = ">=1.35.0"


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
        "with_spirv_tools": [True, False],
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_spirv_tools": True,
        "tools": True,
    }

    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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
        return 11 if tools.Version(self.version) < "1.1.9" else 17

    def export(self):
        self.copy(self._dependencies_filename, src="dependencies", dst="dependencies")

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("cereal/1.3.1")
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
        if tools.Version(self.version) >= "1.0.42" and self.options.shared:
            if tools.Version(self.settings.compiler.version) < "12.0":
                compatible_pkg = self.info.clone()
                compatible_pkg.settings.compiler.version = "12.0"
                self.compatible_packages.append(compatible_pkg)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, self._min_cppstd)
        if self.settings.os not in ["Macos", "iOS", "tvOS"]:
            raise ConanInvalidConfiguration("MoltenVK only supported on MacOS, iOS and tvOS")
        if self.settings.compiler != "apple-clang":
            raise ConanInvalidConfiguration("MoltenVK requires apple-clang")
        if tools.Version(self.version) >= "1.0.42":
            if tools.Version(self.settings.compiler.version) < "12.0":
                raise ConanInvalidConfiguration("MoltenVK {} requires XCode 12.0 or higher at build time".format(self.version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["MVK_VERSION"] = self.version
        cmake.definitions["MVK_WITH_SPIRV_TOOLS"] = self.options.with_spirv_tools
        cmake.definitions["MVK_BUILD_SHADERCONVERTER_TOOL"] = self.options.tools
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["MoltenVK"]
        self.cpp_info.frameworks = ["Metal", "Foundation", "QuartzCore", "IOSurface", "CoreGraphics"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["AppKit", "IOKit"])
        elif self.settings.os in ["iOS", "tvOS"]:
            self.cpp_info.frameworks.append("UIKit")

        if self.options.shared:
            moltenvk_icd_path = os.path.join(self.package_folder, "lib", "MoltenVK_icd.json")
            self.output.info("Prepending to VK_ICD_FILENAMES runtime environment variable: {}".format(moltenvk_icd_path))
            self.runenv_info.prepend_path("VK_ICD_FILENAMES", moltenvk_icd_path)
            # TODO: to remove after conan v2, it allows to not break consumers still relying on virtualenv generator
            self.env_info.VK_ICD_FILENAMES.append(moltenvk_icd_path)

        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
