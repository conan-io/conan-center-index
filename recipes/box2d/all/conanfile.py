import os
from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, rm, rmdir, copy
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class Box2dConan(ConanFile):
    name = "box2d"
    description = "Box2D is a 2D physics engine for games"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://box2d.org/"
    topics = ("physics-engine", "graphic", "2d", "collision")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.variables["BOX2D_BUILD_TESTBED"] = False
        tc.variables["BOX2D_BUILD_UNIT_TESTS"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "box2d"
        self.cpp_info.names["cmake_find_package_multi"] = "box2d"
        self.cpp_info.libs = ["box2d"]
        if Version(self.version) >= "2.4.1" and self.options.shared:
            self.cpp_info.defines.append("B2_SHARED")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
