import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime

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
        cmake_layout(self)

    def requirements(self):
        self.requires("tinyxml/2.6.2", transitive_headers=True, transitive_libs=True)
        self.requires("console_bridge/1.0.2")

    def build_requirements(self):
        if self._tests_enabled:
            self.test_requires("gtest/1.13.0")

    def source(self):
        # urdfdom packages its headers separately as urdfdom_headers.
        # There is no obvious benefit of doing the same for the Conan package,
        # so we simply merge the headers and the main source tree.
        sources = self.conan_data["sources"][self.version]
        get(self, **sources["urdfdom_headers"], strip_root=True, destination="urdf_parser")
        get(self, **sources["urdfdom"], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.variables["APPEND_PROJECT_NAME_TO_INCLUDEDIR"] = False
        tc.variables["BUILD_TESTING"] = self._tests_enabled
        tc.variables["BUILD_APPS"] = False
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        if self._tests_enabled:
            cmake.test()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = [
            "urdfdom_model",
            "urdfdom_model_state",
            "urdfdom_sensor",
            "urdfdom_world",
        ]
