from conans import ConanFile, CMake, tools
from conans.errors import ConanException


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _tested_modules(self):
        return [
            # Main modules
            "calib3d", "core", "dnn", "features2d", "flann", "gapi", "highgui", "imgcodecs",
            "imgproc", "ml", "objdetect", "photo", "stitching", "video", "videoio",
            # Extra modules
            "alphamat", "aruco", "bgsegm", "bioinspired", "ccalib", "datasets", "dnn_superres",
            "face", "freetype", "fuzzy", "hdf", "hfs", "img_hash", "intensity_transform",
            "line_descriptor", "mcc", "optflow", "phase_unwrapping", "plot", "quality", "reg",
            "rgbd", "saliency", "sfm", "shape", "structured_light", "superres",
            "surface_matching", "text", "tracking", "wechat_qrcode", "xfeatures2d",
            "ximgproc", "xobjdetect", "xphoto",
        ]

    def _opencv_option(self, name, default):
        try:
            return getattr(self.options["opencv"], name, default)
        except (AttributeError, ConanException):
            return default

    def build(self):
        cmake = CMake(self)
        for module in self._tested_modules:
            cmake_option = f"OPENCV_WITH_{module.upper()}"
            if module == "core":
                cmake.definitions[cmake_option] = True
            elif module == "imgcodecs":
                cmake.definitions[cmake_option] = self.options["opencv"].imgcodecs and self.options["opencv"].with_png
            elif module == "videoio":
                cmake.definitions[cmake_option] = self.options["opencv"].videoio and self.options["opencv"].with_ffmpeg
            else:
                cmake.definitions[cmake_option] = self._opencv_option(module, False)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(f"ctest --output-on-failure -C {self.settings.build_type} -j {tools.cpu_count()}", run_environment=True)
