import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm

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

    def configure(self):
        # freeimage/3.18.0 still uses openexr/2.x, while opencv defaults to openexr/3.x.
        self.options["opencv"].with_openexr = False

    def requirements(self):
        self.requires("opencv/[>=4.11.0 <5]", transitive_libs=True)
        self.requires("freeimage/3.18.0", transitive_libs=True)
        # freeimage/3.18.0 pins libjpeg/9e, openjpeg/2.5.2, libtiff/4.6.0, libwebp/1.3.2; opencv uses
        # wider ranges that resolve to newer minors on CCI — force a single version in the graph.
        self.requires("libjpeg/9e", override=True)
        self.requires("openjpeg/2.5.2", override=True)
        self.requires("libtiff/4.6.0", override=True)
        self.requires("libwebp/1.3.2", override=True)

    def validate(self):
        check_min_cppstd(self, 17)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.30 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Honor Conan install prefix; upstream forces CMAKE_INSTALL_PREFIX from this cache entry.
        tc.cache_variables["INSTALL_PREFIX_OVERRIDE"] = self.package_folder.replace("\\", "/")
        tc.cache_variables["CMAKE_FIND_PACKAGE_PREFER_CONFIG"] = True
        tc.generate()
        CMakeDeps(self).generate()

    def build(self):
        apply_conandata_patches(self)
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
        if not self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("OPENLQM_STATIC")

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
