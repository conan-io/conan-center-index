import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.scm import Version

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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) >= "4.0":
            self.requires("tinyxml2/10.0.0", transitive_headers=True, transitive_libs=True)
        else:
            self.requires("tinyxml/2.6.2", transitive_headers=True, transitive_libs=True)
        self.requires("console_bridge/1.0.2")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        # urdfdom packages its headers separately as urdfdom_headers.
        # There is no obvious benefit of doing the same for the Conan package,
        # so we simply merge the headers into the main source tree.
        sources = self.conan_data["sources"][self.version]
        get(self, **sources["urdfdom_headers"], strip_root=True,
            destination=os.path.join(self.source_folder, "urdf_parser"))
        get(self, **sources["urdfdom"], strip_root=True, destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["APPEND_PROJECT_NAME_TO_INCLUDEDIR"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_APPS"] = False
        if not self.options.shared:
            tc.preprocessor_definitions["URDFDOM_STATIC"] = "1"
        # Need to set CMP0077 because CMake policy version is too old (3.5 as of v4.0.0)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        CMakeDeps(self).generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
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
        # Copy urdfdom_headers
        copy(self, "*",
             src=os.path.join(self.source_folder, "urdf_parser", "include"),
             dst=os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "urdfdom"))
        rmdir(self, os.path.join(self.package_folder, "CMake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = [
            "urdfdom_model",
            "urdfdom_model_state",
            "urdfdom_sensor",
            "urdfdom_world",
        ]

        if not self.options.shared:
            self.cpp_info.defines.append("URDFDOM_STATIC=1")
