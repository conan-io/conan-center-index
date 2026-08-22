import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd


required_conan_version = ">=2.1"

class ThreeppRecipe(ConanFile):
    name = "threepp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/markaren/threepp"
    description = (
        "Cross-platform C++20 port of the popular Javascript 3D library three.js"
    )
    topics = ("threejs", "opengl", "3d-graphics")
    package_type = "library"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    implements = ["auto_shared_fpic"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {"shared": False, "fPIC": True}

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # INFO: Let Conan manage the C++ standard to be used
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD 20)", "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["THREEPP_BUILD_TESTS"] = False
        tc.cache_variables["THREEPP_BUILD_EXAMPLES"] = False
        tc.cache_variables["THREEPP_USE_EXTERNAL_GLFW"] = True
        
        deps = CMakeDeps(self)
        deps.generate()
        tc.generate()

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.19]")

    def requirements(self):
        self.requires("glfw/3.4")

    def validate(self):
        check_min_cppstd(self, 20)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["threepp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl"]

