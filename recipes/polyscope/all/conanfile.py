import os
import textwrap
from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, save, rm, apply_conandata_patches, export_conandata_patches, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class PolyscopeConan(ConanFile):
    name = "polyscope"
    description = "A viewer for 3D data like meshes and point clouds"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://polyscope.run"
    topics = ("3d", "visualization", "meshes", "point-clouds")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "backend_glfw": [True, False],
        "backend_egl": [True, False],
        "backend_mock": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "backend_glfw": True,
        "backend_egl": True,
        "backend_mock": True,
    }

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
        }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.backend_egl

    def configure(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # The project does not export the necessary symbols for a shared build
            self.package_type = "static-library"
            del self.options.shared
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.backend_glfw:
            self.requires("glfw/3.4", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("backend_egl"):
            self.requires("egl/system", transitive_headers=True, transitive_libs=True)
        if self.options.backend_glfw or self.options.get_safe("backend_egl"):
            self.requires("glad/0.1.36")
        self.requires("glm/1.0.1", transitive_headers=True, transitive_libs=True)
        self.requires("imgui/1.90.5", transitive_headers=True, transitive_libs=True)
        self.requires("nlohmann_json/3.11.3")
        # Using a newer unvendored stb causes "undefined symbol" errors on Windows
        # self.requires("stb/cci.20240531")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_PROJECT_polyscope_INCLUDE"] = "conan_deps.cmake"
        tc.variables["POLYSCOPE_BACKEND_OPENGL3_GLFW"] = self.options.backend_glfw
        tc.variables["POLYSCOPE_BACKEND_OPENGL3_EGL"] = self.options.get_safe("backend_egl", False)
        tc.variables["POLYSCOPE_BACKEND_OPENGL_MOCK"] = self.options.backend_mock
        tc.variables["HAVE_EGL_LIB"] = self.options.get_safe("backend_egl", False)  # Skip EGL/egl.h check for libglvnd
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        if self.settings.os == "Windows" and not self.options.get_safe("shared"):
            # Avoid the default IMGUI_API=__declspec(dllimport)
            tc.preprocessor_definitions["IMGUI_API"] = ""
        # #error "GLM: GLM_GTX_norm is an experimental extension and may change in the future.
        #         Use #define GLM_ENABLE_EXPERIMENTAL before including it, if you really want to use it."
        tc.preprocessor_definitions["GLM_ENABLE_EXPERIMENTAL"] = ""
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("glad", "cmake_target_name", "glad")
        deps.set_property("glfw", "cmake_target_name", "glfw")
        deps.set_property("egl", "cmake_target_name", "EGL")
        deps.set_property("imgui", "cmake_target_name", "imgui")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        copy(self, "*",
             os.path.join(self.dependencies["imgui"].package_folder, "res", "bindings"),
             os.path.join(self.source_folder, "include", "backends"))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # The project does not define any CMake targets
        self.cpp_info.libs = ["polyscope"]
        self.cpp_info.defines.append("GLM_ENABLE_EXPERIMENTAL")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        elif is_apple_os(self):
            self.cpp_info.frameworks = ["Cocoa", "OpenGL", "CoreVideo", "IOKit"]
