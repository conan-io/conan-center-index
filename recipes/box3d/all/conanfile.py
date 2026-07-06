import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

required_conan_version = ">=2.4"


class Box3dConan(ConanFile):
    name = "box3d"
    description = "Box3D is a 3D physics engine for games"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://box2d.org/"
    topics = ("physics-engine", "graphic", "3d", "collision")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_simd": [True, False],
        "double_precision": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_simd": False,
        "double_precision": False,
    }

    implements = ["auto_shared_fpic"]

    def validate(self):
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BOX3D_DISABLE_SIMD"] = self.options.disable_simd
        tc.cache_variables["BOX3D_DOUBLE_PRECISION"] = self.options.double_precision
        tc.cache_variables["BOX3D_COMPILE_WARNING_AS_ERROR"] = False
        tc.cache_variables["BOX3D_SANITIZE"] =  False
        tc.cache_variables["BOX3D_SAMPLES"] = False
        tc.cache_variables["BOX3D_BENCHMARKS"] = False
        tc.cache_variables["BOX3D_DOCS"] = False
        tc.cache_variables["BOX3D_PROFILE"] = False
        # Off by default, not set so that users can override from profile,
        # useful only in Debug builds
        # tc.cache_variables["BOX3D_VALIDATE"] = False
        tc.cache_variables["BOX3D_UNIT_TESTS"] = False
        tc.cache_variables["BOX3D_BUILD_SHADERS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "box3d")
        self.cpp_info.set_property("cmake_target_name", "box3d::box3d")
        self.cpp_info.libs = ["box3d"]
        if self.options.double_precision:
            self.cpp_info.defines.append("BOX3D_DOUBLE_PRECISION")
        if self.options.shared and self.settings.compiler == "msvc":
            self.cpp_info.defines.append("BOX3D_DLL")
