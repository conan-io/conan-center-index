import os
from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, export_conandata_patches, apply_conandata_patches

required_conan_version = ">=1.53.0"


class DawnConan(ConanFile):
    name = "dawn"
    description = ("Dawn is an open-source and cross-platform implementation of the work-in-progress WebGPU standard."
                   " It exposes a C/C++ API that maps almost one-to-one to the WebGPU IDL and"
                   " can be managed as part of a larger system such as a Web browser.")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://dawn.googlesource.com/dawn"
    topics = ("webgpu", "graphics", "gpgpu")

    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("abseil/20240116.2")
        self.requires("spirv-headers/1.3.268.0", transitive_headers=True)
        self.requires("spirv-tools/1.3.268.0")
        self.requires("glslang/1.3.268.0")
        self.requires("glfw/3.4")
        self.requires("vulkan-headers/1.3.268.0")
        self.requires("vulkan-utility-libraries/1.3.268.0")
        self.requires("opengl-registry/20240721")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

        if self.dependencies["spirv-tools"].options.shared:
            raise ConanInvalidConfiguration("spirv-tools must be built as a static library (-o spirv-tools/*:shared=False)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Dawn uses SPIRV-Tools internals, so we need to provide a vendored version
        get(self, **self.conan_data["spirv-tools-sources"][str(self.dependencies["spirv-tools"].ref.version)], strip_root=True,
            destination=os.path.join(self.source_folder, "third_party", "spirv-tools", "src"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DAWN_BUILD_MONOLITHIC_LIBRARY"] = True  # TODO: the default behavior, but might want to expose as an option
        tc.variables["DAWN_ENABLE_INSTALL"] = True
        tc.variables["DAWN_BUILD_SAMPLES"] = False
        tc.variables["TINT_ENABLE_INSTALL"] = False
        tc.variables["TINT_BUILD_TESTS"] = False
        tc.variables["SPIRV_TOOLS_BUILD_STATIC"] = True
        tc.variables["SPIRV-Headers_SOURCE_DIR"] = self.dependencies["spirv-headers"].package_folder.replace("\\", "/")
        tc.variables["OPENGL_REGISTRY_DATA_DIR"] = self.dependencies["opengl-registry"].cpp_info.resdirs[0].replace("\\", "/")
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("spirv-headers", "cmake_target_name", "SPIRV-Headers")
        deps.set_property("glslang", "cmake_target_name", "glslang")
        deps.set_property("glslang::glslang-default-resource-limits", "cmake_target_name", "glslang-default-resource-limits")
        deps.set_property("glfw", "cmake_target_name", "glfw")
        deps.set_property("vulkan-headers", "cmake_file_name", "Vulkan-Headers")
        deps.set_property("vulkan-headers", "cmake_target_name", "Vulkan-Headers")
        deps.set_property("vulkan-utility-libraries::VulkanUtilityHeaders", "cmake_target_name", "VulkanUtilityHeaders")
        # Hide the spirv-tools components transitively exposed by glslang to avoid conflicts with the vendored version
        for component in ["core", "diff", "link", "lint", "opt", "reduce"]:
            deps.set_property(f"spirv-tools::spirv-tools-{component}", "cmake_target_name", f"SPIRV-Tools-{component}_private")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Make sure everything is unvendored
        for path in Path(self.source_folder, "third_party").iterdir():
            if path.is_dir() and path.name != "spirv-tools":
                rmdir(self, path)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Dawn")
        self.cpp_info.set_property("cmake_target_name", "dawn::webgpu_dawn")
        self.cpp_info.libs = ["webgpu_dawn"]
