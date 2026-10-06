import json
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_max_cppstd, check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, load, replace_in_file, rm, rmdir

required_conan_version = ">=2.1"

class OpenUSDConan(ConanFile):
    name = "openusd"
    description = "Universal Scene Description"
    license = "LicenseRef-TOST-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://openusd.org/"
    topics = ("3d", "scene", "usd")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_imaging": [True, False],
        "with_openimageio": [True, False],
        "with_materialx": [True, False],
    }
    default_options = {
        "with_imaging": True,
        "with_openimageio": False,
        "with_materialx": False,
    }
    exports = "components/*.json"

    def configure(self):
        if not self.options.with_imaging:
            self.options.rm_safe("with_openimageio")
        if self.options.with_materialx:
            self.options["materialx"].shared = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("onetbb/2023.1.0", transitive_headers=True)
        if self.options.with_imaging:
            self.requires("opensubdiv/3.7.0")
            self.requires("opengl/system")
            if self.settings.os == "Linux":
                self.requires("xorg/system")
        if self.options.get_safe("with_openimageio"):
            self.requires("openimageio/2.5.19.1")
        if self.options.with_materialx:
            self.requires("materialx/1.39.4")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.27]")

    def validate(self):
        check_min_cppstd(self, 17)
        if self.options.with_imaging and not self.dependencies["opensubdiv"].options.with_opengl:
            raise ConanInvalidConfiguration('openusd requires -o "opensubdiv/*:with_opengl=True"')
        if self.options.with_materialx and not self.dependencies["materialx"].options.shared:
            raise ConanInvalidConfiguration('openusd requires -o "materialx/*:shared=True"')

    def validate_build(self):
        check_max_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "defaults", "CXXDefaults.cmake"),
                        "set(CMAKE_CXX_STANDARD 17)\nset(CMAKE_CXX_STANDARD_REQUIRED ON)\nset(CMAKE_CXX_EXTENSIONS OFF)\n", "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["PXR_BUILD_USDVIEW"] = False
        tc.cache_variables["PXR_BUILD_TESTS"] = False
        tc.cache_variables["PXR_BUILD_EXAMPLES"] = False
        tc.cache_variables["PXR_BUILD_TUTORIALS"] = False
        tc.cache_variables["PXR_ENABLE_PYTHON_SUPPORT"] = False
        tc.cache_variables["PXR_BUILD_USD_TOOLS"] = False
        tc.cache_variables["PXR_BUILD_IMAGING"] = self.options.with_imaging
        tc.cache_variables["PXR_BUILD_USD_IMAGING"] = self.options.with_imaging
        tc.cache_variables["PXR_BUILD_OPENIMAGEIO_PLUGIN"] = bool(self.options.get_safe("with_openimageio"))
        tc.cache_variables["PXR_ENABLE_MATERIALX_SUPPORT"] = self.options.with_materialx
        if self.options.get_safe("with_openimageio"):
            tc.cache_variables["OIIO_LIBRARIES"] = "OpenImageIO::OpenImageIO"
        tc.generate()

        deps = CMakeDeps(self)
        if self.options.with_imaging:
            subdiv_suffix = "" if self.dependencies["opensubdiv"].options.shared else "_static"
            deps.set_property("opensubdiv::osdcpu", "cmake_target_name", f"OpenSubdiv::osdCPU{subdiv_suffix}")
            deps.set_property("opensubdiv::osdgpu", "cmake_target_name", f"OpenSubdiv::osdGPU{subdiv_suffix}")

        if self.options.with_materialx:
            # Remove materialx namespace
            materialx_targets = [
                "MaterialXCore",
                "MaterialXFormat",
                "MaterialXGenGlsl",
                "MaterialXGenOsl",
                "MaterialXGenMsl",
                "MaterialXGenShader",
                "MaterialXRender",
                "MaterialXRenderGlsl",
            ]
            for target in materialx_targets:
                deps.set_property(f"materialx::{target}", "cmake_target_name", target)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "NOTICE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rm(self, "pxrConfig.cmake", self.package_folder)
        rmdir(self, os.path.join(self.package_folder, "cmake"))

    @property
    def _components_file(self):
        return os.path.join(self.recipe_folder, "components", f"{self.version}.json")

    @property
    def _components_info(self):
        # extracted from upstream's own CMakeLists.txt files
        return json.loads(load(self, self._components_file))

    def _condition_is_true(self, condition):
        symbols = {
            "is_apple": is_apple_os(self),
            "with_imaging": bool(self.options.with_imaging),
            "with_openimageio": bool(self.options.get_safe("with_openimageio")),
            "with_materialx": bool(self.options.with_materialx),
        }
        return all(symbols[name] for name in condition)

    def package_info(self):
        is_apple = is_apple_os(self)
        kit_framework = "AppKit" if self.settings.os == "Macos" else "UIKit"
        plugin_dir = os.path.join("plugin", "usd")

        for comp_name, comp_info in self._components_info.items():
            if not self._condition_is_true(comp_info.get("condition", [])):
                continue

            requires = list(comp_info.get("requires", []))
            frameworks = list(comp_info.get("frameworks", []))
            for extra in comp_info.get("conditional", []):
                if self._condition_is_true(extra["condition"]):
                    requires.extend(extra.get("requires", []))
                    frameworks.extend(extra.get("frameworks", []))
            frameworks = [kit_framework if f == "$kit_framework" else f for f in frameworks]

            is_plugin = comp_info.get("is_plugin", False)
            component = self.cpp_info.components[comp_name]
            component.requires = requires
            if is_apple:
                component.frameworks = frameworks
            if is_plugin:
                # Loaded dynamically at runtime through USD's Plug registry
                # (plugInfo.json), never linked directly: no .libs, just the
                # location so it's still discoverable/dlopen-able.
                component.libdirs = [plugin_dir]
                component.bindirs = [plugin_dir]
            else:
                component.libs = [f"usd_{comp_name}"]
                if self.settings.os == "Windows":
                    component.bindirs = ["lib"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["arch"].system_libs = ["m", "pthread", "dl"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["arch"].system_libs = ["ws2_32", "dbghelp"]

        if self.options.with_imaging and self.settings.os == "Linux":
            self.cpp_info.components["garch"].requires.append("xorg::x11")
