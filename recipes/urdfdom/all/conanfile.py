import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    replace_in_file,
    rm,
)

required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "urdfdom"
    description = "Data structures and parsers to access URDF files using the DOM model"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ros/urdfdom"
    topics = ("urdf", "ros", "robotics")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _tests_enabled(self):
        return not self.conf.get("tools.build:skip_test", default=True, check_type=bool)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["tinyxml"].with_stl = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("tinyxml/2.6.2", transitive_headers=True, transitive_libs=True)
        self.requires("console_bridge/1.0.2")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def build_requirements(self):
        if self._tests_enabled:
            self.build_requires("gtest/1.13.0")

    def source(self):
        # urdfdom packages its headers separately as urdfdom_headers.
        # There is no obvious benefit of doing the same for the Conan package,
        # so we simply merge the headers into the main source tree.
        sources = self.conan_data["sources"][self.version]
        get(
            self,
            **sources["urdfdom_headers"],
            strip_root=True,
            destination=os.path.join(self.source_folder, "urdf_parser"),
        )
        get(self, **sources["urdfdom"], strip_root=True, destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["APPEND_PROJECT_NAME_TO_INCLUDEDIR"] = False
        tc.variables["BUILD_TESTING"] = self._tests_enabled
        tc.variables["BUILD_APPS"] = False
        if not self.options.shared:
            tc.preprocessor_definitions["URDFDOM_STATIC"] = "1"
        tc.generate()
        CMakeDeps(self).generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Do not hard-code libraries to SHARED
        replace_in_file(
            self,
            os.path.join(self.source_folder, "urdf_parser", "CMakeLists.txt"),
            " SHARED",
            "",
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if self._tests_enabled:
            cmake.test()

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()

        rm(self, "*.pdb", self.package_folder)

    def package_info(self):
        self.cpp_info.libs = [
            "urdfdom_model",
            "urdfdom_model_state",
            "urdfdom_sensor",
            "urdfdom_world",
        ]

        self.cpp_info.set_property("cmake_module_file_name", "urdfdom")
        self.cpp_info.set_property("cmake_module_target_name", "urdfdom::urdfdom")
        self.cpp_info.set_property("cmake_file_name", "urdfdom")
        self.cpp_info.set_property("cmake_target_name", "urdfdom::urdfdom")
        self.cpp_info.set_property("pkg_config_name", "urdfdom")

        if not self.options.shared:
            self.cpp_info.defines.append("URDFDOM_STATIC=1")
