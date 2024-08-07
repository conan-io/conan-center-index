import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir

required_conan_version = ">=1.53.0"


class MagnumIntegrationConan(ConanFile):
    name = "magnum-integration"
    description = "Integration libraries for the Magnum C++11/C++14 graphics engine"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://magnum.graphics"
    topics = ("magnum", "graphics", "rendering", "3d", "2d", "opengl")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_bullet": [True, False],
        "with_dart": [True, False],
        "with_eigen": [True, False],
        "with_glm": [True, False],
        "with_imgui": [True, False],
        "with_ovr": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_bullet": True,
        "with_dart": False,
        "with_eigen": True,
        "with_glm": True,
        "with_imgui": True,
        "with_ovr": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"magnum/{self.version}", transitive_headers=True, transitive_libs=True)
        if self.options.with_bullet:
            # Used in Magnum/BulletIntegration/Integration.h
            self.requires("bullet3/3.25", transitive_headers=True, transitive_libs=True)
        if self.options.with_eigen:
            # Used in Magnum/EigenIntegration/Integration.h
            self.requires("eigen/3.4.0", transitive_headers=True)
        if self.options.with_glm:
            # Used in Magnum/GlmIntegration/Integration.h
            self.requires("glm/cci.20230113", transitive_headers=True, transitive_libs=True)
        if self.options.with_imgui:
            # Used in Magnum/ImGuiIntegration/Integration.h
            self.requires("imgui/1.90", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.options.with_dart:
            # FIXME: Add 'dart' requirement
            raise ConanInvalidConfiguration("DART library is not available in ConanCenter (yet)")
        if self.options.with_ovr:
            # FIXME: Add 'ovr' requirement
            raise ConanInvalidConfiguration("OVR library is not available in ConanCenter (yet)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.variables["BUILD_STATIC_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_GL_TESTS"] = False
        tc.variables["WITH_BULLET"] = self.options.with_bullet
        tc.variables["WITH_DART"] = self.options.with_dart
        tc.variables["WITH_EIGEN"] = self.options.with_eigen
        tc.variables["WITH_GLM"] = self.options.with_glm
        tc.variables["WITH_IMGUI"] = self.options.with_imgui
        tc.variables["WITH_OVR"] = self.options.with_ovr
        tc.variables["MAGNUM_INCLUDE_INSTALL_DIR"] = "include/Magnum"
        tc.variables["MAGNUM_EXTERNAL_INCLUDE_INSTALL_DIR"] = "include/MagnumExternal"
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("glm", "cmake_file_name", "GLM")
        deps.set_property("glm", "cmake_target_name", "GLM::GLM")
        deps.set_property("imgui", "cmake_file_name", "ImGui")
        deps.set_property("imgui", "cmake_target_name", "ImGui::ImGui")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "src", "Magnum", "ImGuiIntegration", "CMakeLists.txt"),
                        "ImGui::Sources", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "MagnumIntegration")
        self.cpp_info.names["cmake_find_package"] = "MagnumIntegration"
        self.cpp_info.names["cmake_find_package_multi"] = "MagnumIntegration"

        lib_suffix = "-d" if self.settings.build_type == "Debug" else ""

        if self.options.with_bullet:
            self.cpp_info.components["bullet"].set_property("cmake_target_name", "MagnumIntegration::Bullet")
            self.cpp_info.components["bullet"].names["cmake_find_package"] = "Bullet"
            self.cpp_info.components["bullet"].names["cmake_find_package_multi"] = "Bullet"
            self.cpp_info.components["bullet"].libs = ["MagnumBulletIntegration{}".format(lib_suffix)]
            self.cpp_info.components["bullet"].requires = [
                "magnum::magnum_main",
                "magnum::gl",
                "magnum::shaders",
                "bullet3::bullet3",
            ]

        if self.options.with_dart:
            raise ConanException("Recipe doesn't define this component 'dart'. Please contribute it")

        if self.options.with_eigen:
            self.cpp_info.components["eigen"].set_property("cmake_target_name", "MagnumIntegration::Eigen")
            self.cpp_info.components["eigen"].names["cmake_find_package"] = "Eigen"
            self.cpp_info.components["eigen"].names["cmake_find_package_multi"] = "Eigen"
            self.cpp_info.components["eigen"].requires = ["magnum::magnum_main", "eigen::eigen"]

        if self.options.with_glm:
            self.cpp_info.components["glm"].set_property("cmake_target_name", "MagnumIntegration::Glm")
            self.cpp_info.components["glm"].names["cmake_find_package"] = "Glm"
            self.cpp_info.components["glm"].names["cmake_find_package_multi"] = "Glm"
            self.cpp_info.components["glm"].libs = [f"MagnumGlmIntegration{lib_suffix}"]
            self.cpp_info.components["glm"].requires = ["magnum::magnum_main", "glm::glm"]

        if self.options.with_imgui:
            self.cpp_info.components["imgui"].set_property("cmake_target_name", "MagnumIntegration::ImGui")
            self.cpp_info.components["imgui"].names["cmake_find_package"] = "ImGui"
            self.cpp_info.components["imgui"].names["cmake_find_package_multi"] = "ImGui"
            self.cpp_info.components["imgui"].libs = [f"MagnumImGuiIntegration{lib_suffix}"]
            self.cpp_info.components["imgui"].requires = [
                "magnum::magnum_main",
                "magnum::gl",
                "magnum::shaders",
                "imgui::imgui",
            ]

        if self.options.with_ovr:
            raise ConanException("Recipe doesn't define this component 'ovr'. Please contribute it")
