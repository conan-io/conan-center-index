import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class TinyDnnConan(ConanFile):
    name = "tiny-dnn"
    description = "tiny-dnn is a C++14 implementation of deep learning."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tiny-dnn/tiny-dnn"
    topics = ("header-only", "deep-learning", "embedded", "iot", "computational")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"with_tbb": [True, False]}
    default_options = {"with_tbb": False}

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cereal/1.3.1")
        self.requires("stb/cci.20210713")
        if self.options.with_tbb:
            self.requires("onetbb/[>=2020.3 <2024]")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_TBB"] = self.options.with_tbb
        tc.variables["USE_GEMMLOWP"] = False
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
        if self.options.with_tbb:
            self.cpp_info.components["tinydnn"].defines = ["CNN_USE_TBB=1"]
            self.cpp_info.components["tinydnn"].requires.append("onetbb::libtbb")
