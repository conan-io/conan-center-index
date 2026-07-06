import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir

required_conan_version = ">=2.1"


class TinyDnnConan(ConanFile):
    name = "tiny-dnn"
    deprecated = "This project is no longer maintained by its authors and is not recommended for us"
    description = "tiny-dnn is a C++14 implementation of deep learning."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tiny-dnn/tiny-dnn"
    topics = ("header-only", "deep-learning", "embedded", "iot", "computational")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cereal/1.3.1")
        self.requires("stb/cci.20210713")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_GEMMLOWP"] = False
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        replace_in_file(self,
                        os.path.join(self.source_folder, "tiny_dnn", "util", "image.h"),
                        "third_party/", "")

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "tinydnn")
        self.cpp_info.set_property("cmake_target_name", "TinyDNN::tiny_dnn")

        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["tinydnn"].set_property("cmake_target_name", "TinyDNN::tiny_dnn")
        self.cpp_info.components["tinydnn"].requires = ["cereal::cereal", "stb::stb"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["tinydnn"].system_libs = ["pthread"]
