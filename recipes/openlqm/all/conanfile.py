import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm

required_conan_version = ">=2.1"


class OpenLqmConan(ConanFile):
    name = "openlqm"
    description = (
        "OpenLQM: a C++ library and CLI for latent-quality (LQ) fingerprint image analysis, "
        "developed for NIST."
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/usnistgov/openlqm"
    topics = ("nist", "fingerprint", "biometrics", "computer-vision", "opencv")

    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def configure(self):
        # freeimage/3.18.0 depends on openexr/2.x; disable openexr in opencv to avoid
        # a version conflict between openexr/2.x and openexr/3.x in the graph.
        self.options["opencv"].with_openexr = False

    def requirements(self):
        self.requires("opencv/[>=4.11.0 <5]", transitive_libs=True)
        self.requires("freeimage/3.18.0", transitive_libs=True)

    def validate(self):
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.30]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Honor Conan install prefix; upstream forces CMAKE_INSTALL_PREFIX from this cache entry.
        tc.cache_variables["INSTALL_PREFIX_OVERRIDE"] = self.package_folder.replace("\\", "/")
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "NOTICE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["openlqm"]

        self.cpp_info.requires = [
            "opencv::opencv_core",
            "opencv::opencv_ml",
            "opencv::opencv_imgproc",
            "opencv::opencv_imgcodecs",
            "freeimage::FreeImage",
        ]

        self.cpp_info.set_property("cmake_file_name", "OpenLQM")
        self.cpp_info.set_property("cmake_target_name", "openlqm::openlqm")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
