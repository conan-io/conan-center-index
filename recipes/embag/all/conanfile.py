import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rm, replace_in_file

required_conan_version = ">=1.53.0"


class EmbagConan(ConanFile):
    name = "embag"
    description = "Schema and dependency free ROS bag reader"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/embarktrucks/embag"
    topics = ("rosbag", "ros", "robotics")
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
        copy(
            self,
            "CMakeLists.txt",
            src=self.recipe_folder,
            dst=os.path.join(self.export_sources_folder, "src"),
        )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.81.0", transitive_headers=True)
        self.requires("lz4/1.9.4", transitive_headers=True, transitive_libs=True)
        self.requires("bzip2/1.0.8", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        # Disable a C++11 workaround that is broken on MSVC
        replace_in_file(
            self,
            os.path.join(self.source_folder, "lib", "util.h"),
            "#if __cplusplus < 201402L",
            "#if false",
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

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
        self.cpp_info.libs = ["embag"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
