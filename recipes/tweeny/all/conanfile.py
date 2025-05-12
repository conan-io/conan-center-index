from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os


required_conan_version = ">=2.0.9"

class TweenyConan(ConanFile):
    name = "tweeny"
    description = "Tweeny is an inbetweening library designed for the creation of complex animations for games and other beautiful interactive software"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mobius3/tweeny"
    topics = ("animation", "tweening", "easing-functions")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"


    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) == "3.2.0":
            # already fixed in master, assuming it is fixed in upcoming release
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"  # CMake 4 support
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package_id(self):
        self.info.clear()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "tweeny")
        self.cpp_info.set_property("cmake_target_name", "tweeny")
