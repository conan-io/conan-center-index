from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration, ConanException
import functools
import os

required_conan_version = ">=1.43.0"


class MagnumIntegrationConan(ConanFile):
    name = "magnum-integration"
    description = "Integration libraries for the Magnum C++11/C++14 graphics engine"
    license = "MIT"
    topics = ("magnum", "graphics", "rendering", "3d", "2d", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://magnum.graphics"

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

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("magnum/{}".format(self.version))
        if self.options.with_bullet:
            self.requires("bullet3/3.22a")
        if self.options.with_eigen:
            self.requires("eigen/3.4.0")
        if self.options.with_glm:
            self.requires("glm/0.9.9.8")
        if self.options.with_imgui:
            self.requires("imgui/1.87")

    def validate(self):
        if self.options.with_dart:
            # FIXME: Add 'dart' requirement
            raise ConanInvalidConfiguration("DART library is not available in ConanCenter (yet)")
        if self.options.with_ovr:
            # FIXME: Add 'ovr' requirement
            raise ConanInvalidConfiguration("OVR library is not available in ConanCenter (yet)")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_STATIC"] = not self.options.shared
        cmake.definitions["BUILD_STATIC_PIC"] = self.options.get_safe("fPIC", True)
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["BUILD_GL_TESTS"] = False

        cmake.definitions["WITH_BULLET"] = self.options.with_bullet
        cmake.definitions["WITH_DART"] = self.options.with_dart
        cmake.definitions["WITH_EIGEN"] = self.options.with_eigen
        cmake.definitions["WITH_GLM"] = self.options.with_glm
        cmake.definitions["WITH_IMGUI"] = self.options.with_imgui
        cmake.definitions["WITH_OVR"] = self.options.with_ovr

        cmake.configure()
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              'set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/modules/" ${CMAKE_MODULE_PATH})',
                              "")
        # Casing
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "GlmIntegration", "CMakeLists.txt"),
                              "find_package(GLM REQUIRED)",
                              "find_package(glm REQUIRED)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "GlmIntegration", "CMakeLists.txt"),
                              "GLM::GLM",
                              "glm::glm")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "ImGuiIntegration", "CMakeLists.txt"),
                              "find_package(ImGui REQUIRED Sources)",
                              "find_package(imgui REQUIRED Sources)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "ImGuiIntegration", "CMakeLists.txt"),
                              "ImGui::ImGui",
                              "imgui::imgui")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "ImGuiIntegration", "CMakeLists.txt"),
                              "ImGui::Sources",
                              "")

    def build(self):
        self._patch_sources()

        cm = self._configure_cmake()
        cm.build()

    def package(self):
        cm = self._configure_cmake()
        cm.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

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
            self.cpp_info.components["bullet"].requires = ["magnum::magnum_main", "magnum::gl", "magnum::shaders", "bullet3::bullet3"]

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
            self.cpp_info.components["glm"].libs = ["MagnumGlmIntegration{}".format(lib_suffix)]
            self.cpp_info.components["glm"].requires = ["magnum::magnum_main", "glm::glm"]

        if self.options.with_imgui:
            self.cpp_info.components["imgui"].set_property("cmake_target_name", "MagnumIntegration::ImGui")
            self.cpp_info.components["imgui"].names["cmake_find_package"] = "ImGui"
            self.cpp_info.components["imgui"].names["cmake_find_package_multi"] = "ImGui"
            self.cpp_info.components["imgui"].libs = ["MagnumImGuiIntegration{}".format(lib_suffix)]
            self.cpp_info.components["imgui"].requires = ["magnum::magnum_main", "magnum::gl", "magnum::shaders", "imgui::imgui"]

        if self.options.with_ovr:
            raise ConanException("Recipe doesn't define this component 'ovr'. Please contribute it")
