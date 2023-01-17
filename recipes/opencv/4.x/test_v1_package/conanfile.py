from conans import ConanFile, CMake, tools
from conans.errors import ConanException


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def _opencv_option(self, name, default):
        try:
            return getattr(self.options["opencv"], name, default)
        except (AttributeError, ConanException):
            return default

    def build(self):
        cmake = CMake(self)
        cmake.definitions["OPENCV_WITH_CALIB3D"] = self.options["opencv"].calib3d
        cmake.definitions["OPENCV_WITH_FEATURES2D"] = self.options["opencv"].features2d
        cmake.definitions["OPENCV_WITH_FLANN"] = self.options["opencv"].flann
        cmake.definitions["OPENCV_WITH_GAPI"] = self.options["opencv"].gapi
        cmake.definitions["OPENCV_WITH_HIGHGUI"] = self.options["opencv"].highgui
        cmake.definitions["OPENCV_WITH_IMGCODECS_PNG"] = self.options["opencv"].imgcodecs and self.options["opencv"].with_png
        cmake.definitions["OPENCV_WITH_IMGPROC"] = self.options["opencv"].imgproc
        cmake.definitions["OPENCV_WITH_ML"] = self.options["opencv"].ml
        cmake.definitions["OPENCV_WITH_OBJDETECT"] = self.options["opencv"].objdetect
        cmake.definitions["OPENCV_WITH_PHOTO"] = self.options["opencv"].photo
        cmake.definitions["OPENCV_WITH_STITCHING"] = self.options["opencv"].stitching
        cmake.definitions["OPENCV_WITH_VIDEO"] = self.options["opencv"].video
        cmake.definitions["OPENCV_WITH_VIDEOIO_FFMPEG"] = self.options["opencv"].videoio and self.options["opencv"].with_ffmpeg
        cmake.definitions["OPENCV_WITH_ALPHAMAT"] = self._opencv_option("alphamat", False)
        cmake.definitions["OPENCV_WITH_ARUCO"] = self.options["opencv"].aruco
        cmake.definitions["OPENCV_WITH_BGSEGM"] = self.options["opencv"].bgsegm
        cmake.definitions["OPENCV_WITH_BIOINSPIRED"] = self.options["opencv"].bioinspired
        cmake.definitions["OPENCV_WITH_FREETYPE"] = self.options["opencv"].freetype
        cmake.definitions["OPENCV_WITH_FUZZY"] = self.options["opencv"].fuzzy
        cmake.definitions["OPENCV_WITH_HFS"] = self.options["opencv"].hfs
        cmake.definitions["OPENCV_WITH_IMG_HASH"] = self.options["opencv"].img_hash
        cmake.definitions["OPENCV_WITH_INTENSITY_TRANSFORM"] = self._opencv_option("intensity_transform", False)
        cmake.definitions["OPENCV_WITH_LINE_DESCRIPTOR"] = self.options["opencv"].line_descriptor
        cmake.definitions["OPENCV_WITH_MCC"] = self._opencv_option("mcc", False)
        cmake.definitions["OPENCV_WITH_OPTFLOW"] = self.options["opencv"].optflow
        cmake.definitions["OPENCV_WITH_PHASE_UNWRAPPING"] = self.options["opencv"].phase_unwrapping
        cmake.definitions["OPENCV_WITH_QUALITY"] = self.options["opencv"].quality
        cmake.definitions["OPENCV_WITH_REG"] = self.options["opencv"].reg
        cmake.definitions["OPENCV_WITH_RGBD"] = self.options["opencv"].rgbd
        cmake.definitions["OPENCV_WITH_SALIENCY"] = self.options["opencv"].saliency
        cmake.definitions["OPENCV_WITH_SFM"] = self.options["opencv"].sfm
        cmake.definitions["OPENCV_WITH_SHAPE"] = self.options["opencv"].shape
        cmake.definitions["OPENCV_WITH_STRUCTURED_LIGHT"] = self.options["opencv"].structured_light
        cmake.definitions["OPENCV_WITH_SUPERRES"] = self._opencv_option("superres", False)
        cmake.definitions["OPENCV_WITH_SURFACE_MATCHING"] = self.options["opencv"].surface_matching
        cmake.definitions["OPENCV_WITH_TEXT"] = self.options["opencv"].text
        cmake.definitions["OPENCV_WITH_TRACKING"] = self.options["opencv"].tracking
        cmake.definitions["OPENCV_WITH_WECHAT_QRCODE"] = self._opencv_option("wechat_qrcode", False)
        cmake.definitions["OPENCV_WITH_XFEATURES2D"] = self.options["opencv"].xfeatures2d
        cmake.definitions["OPENCV_WITH_XIMGPROC"] = self.options["opencv"].ximgproc
        cmake.definitions["OPENCV_WITH_XOBJDETECT"] = self.options["opencv"].xobjdetect
        cmake.definitions["OPENCV_WITH_XPHOTO"] = self.options["opencv"].xphoto
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(f"ctest --output-on-failure -C {self.settings.build_type} -j {tools.cpu_count()}", run_environment=True)
