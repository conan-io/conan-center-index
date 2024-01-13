from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def configure(self):
        self.options["cimg"].enable_curl = True
        self.options["cimg"].enable_display = True
        self.options["cimg"].enable_ffmpeg = True
        self.options["cimg"].enable_fftw = True
        self.options["cimg"].enable_heif = True
        self.options["cimg"].enable_jpeg = "libjpeg"
        self.options["cimg"].enable_magick = False # Not yet Conan 2.0 compatible
        self.options["cimg"].enable_opencv = False # OpenCV v3 Requires OpenEXR v2
        self.options["cimg"].enable_openexr = True
        self.options["cimg"].enable_openmp = True
        self.options["cimg"].enable_png = True
        self.options["cimg"].enable_tiff = True
        self.options["cimg"].enable_tinyexr = False # Conflicts with OpenEXR and ZLib
        self.options["cimg"].enable_xrandr = True
        self.options["cimg"].enable_xshm = True
        self.options["cimg"].enable_zlib = True

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
