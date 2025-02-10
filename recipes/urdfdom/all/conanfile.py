import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


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
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("urdfdom_headers/1.1.1", transitive_headers=True)
        self.requires("console_bridge/1.0.2")
        if Version(self.version) >= "4.0":
            self.requires("tinyxml2/10.0.0")
        else:
            self.requires("tinyxml/2.6.2", transitive_headers=True, transitive_libs=True)

    def validate(self):
        check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["APPEND_PROJECT_NAME_TO_INCLUDEDIR"] = True
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_APPS"] = False
        if not self.options.shared:
            tc.preprocessor_definitions["URDFDOM_STATIC"] = "1"
        # Need to set CMP0077 because CMake policy version is too old (3.5 as of v4.0.0)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        CMakeDeps(self).generate()

    def _patch_sources(self):
        # Do not hard-code libraries to SHARED
        parser_cmakelists = os.path.join(self.source_folder, "urdf_parser", "CMakeLists.txt")
        replace_in_file(self, parser_cmakelists, " SHARED", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "urdfdom"))
        rmdir(self, os.path.join(self.package_folder, "CMake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "urdfdom")
        self.cpp_info.set_property("cmake_target_name", "urdfdom::urdf_parser")
        self.cpp_info.set_property("pkg_config_name", "urdfdom")
        # For backwards compatibility with the previously incorrectly exported target name
        self.cpp_info.set_property("cmake_target_aliases", ["urdfdom::urdfdom"])

        def _add_component(lib, requires=None):
            component = self.cpp_info.components[lib]
            component.set_property("cmake_target_name", f"urdfdom::{lib}")
            component.includedirs.append(os.path.join("include", "urdfdom"))
            component.libs.append(lib)
            component.requires += [
                "urdfdom_headers::urdfdom_headers",
                "console_bridge::console_bridge",
            ]
            if Version(self.version) >= "4.0":
                component.requires.append("tinyxml2::tinyxml2")
            else:
                component.requires.append("tinyxml::tinyxml")
            if requires:
                component.requires.extend(requires)

        _add_component("urdfdom_model")
        _add_component("urdfdom_model_state")
        _add_component("urdfdom_sensor", requires=["urdfdom_model"])
        _add_component("urdfdom_world")

        if not self.options.shared:
            self.cpp_info.defines.append("URDFDOM_STATIC=1")
