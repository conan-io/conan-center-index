from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, rm, replace_in_file
from conan.tools.scm import Version

import os

required_conan_version = ">=2.1"


class TesseractConan(ConanFile):
    name = "tesseract"
    description = "Tesseract Open Source OCR Engine"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tesseract-ocr/tesseract"
    topics = ("ocr", "image", "multimedia", "graphics")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_auto_optimize": [True, False],
        "with_march_native": [True, False],
        "with_training": [True, False],
        "with_libcurl": [True, False],
        "with_libarchive": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_auto_optimize": False,
        "with_march_native": False,
        "with_training": False,
        "with_libcurl": True,
        "with_libarchive": True,
    }

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
        if Version(self.version) >= "5.2.0":
            self.requires("leptonica/1.83.1")
        else:
            self.requires("leptonica/1.82.0")
        if self.settings.os == "Windows":
            self.requires("libtiff/4.6.0")
        # libarchive is required for 4.x so default value is true
        if self.options.get_safe("with_libarchive", default=True):
            self.requires("libarchive/3.7.2")
        # libcurl is not required for 4.x
        if self.options.get_safe("with_libcurl", default=False):
            self.requires("libcurl/[>=7.78.0 <9]")

    def validate(self):
        check_min_cppstd(self, "17")

        if self.options.with_training:
            # do not enforce failure and allow user to build with system cairo, pango, fontconfig
            self.output.warning("*** Build with training is not yet supported, continue on your own")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TRAINING_TOOLS"] = self.options.with_training
        tc.variables["INSTALL_CONFIGS"] = self.options.with_training
        # Use CMake-based package build and dependency detection, not the pkg-config, cppan or SW
        tc.variables["CPPAN_BUILD"] = False
        tc.variables["SW_BUILD"] = False
        # disable autodetect of vector extensions and march=native
        tc.variables["ENABLE_OPTIMIZATIONS"] = self.options.with_auto_optimize
        # Set Leptonica_DIR to ensure that find_package will be called in original CMake file
        tc.variables["Leptonica_DIR"] = self.dependencies["leptonica"].package_folder.replace("\\", "/")
        tc.variables["DISABLE_CURL"] = not self.options.with_libcurl
        tc.variables["DISABLE_ARCHIVE"] = not self.options.with_libarchive
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        if self.dependencies["leptonica"].options.get_safe("with_tiff"):
            # version <=5.2 do not contain this check, and if not replaced it fail, strict=False is safe
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), 
                            "check_leptonica_tiff_support()", "", strict=False)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        # Official CMake imported target is:
        # - libtesseract if < 5.0.0
        # - Tesseract::libtesseract if >= 5.0.0
        # We provide both targets
        self.cpp_info.set_property("cmake_file_name", "Tesseract")
        self.cpp_info.set_property("cmake_target_name", "Tesseract::libtesseract")
        self.cpp_info.set_property("cmake_target_aliases", ["libtesseract"])
        self.cpp_info.set_property("pkg_config_name", "tesseract")

        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["libtesseract"].libs = [self._libname]
        self.cpp_info.components["libtesseract"].requires = ["leptonica::leptonica"]
        if self.settings.os == "Windows":
            self.cpp_info.components["libtesseract"].requires.append("libtiff::libtiff")
        if self.options.get_safe("with_libcurl", default=False):
            self.cpp_info.components["libtesseract"].requires.append("libcurl::libcurl")
        if self.options.get_safe("with_libarchive", default=True):
            self.cpp_info.components["libtesseract"].requires.append("libarchive::libarchive")
        if self.options.shared:
            self.cpp_info.components["libtesseract"].defines = ["TESS_IMPORTS"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libtesseract"].system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["libtesseract"].system_libs = ["ws2_32"]
        self.cpp_info.components["libtesseract"].set_property("pkg_config_name", "tesseract")

    @property
    def _libname(self):
        suffix = ""
        if self.settings.os == "Windows":
            v = Version(self.version)
            suffix += f"{v.major}{v.minor}"
            if self.settings.build_type == "Debug":
                suffix += "d"
        return f"tesseract{suffix}"
