from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

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
        cmake.definitions["OPENCV_WITH_ARUCO"] = self.options["opencv"].aruco
        cmake.definitions["OPENCV_WITH_BGSEGM"] = self.options["opencv"].bgsegm
        cmake.definitions["OPENCV_WITH_FREETYPE"] = self.options["opencv"].freetype
        cmake.definitions["OPENCV_WITH_IMG_HASH"] = self.options["opencv"].img_hash
        cmake.definitions["OPENCV_WITH_INTENSITY_TRANSFORM"] = tools.Version(self.deps_cpp_info["opencv"].version) >= "4.3.0" and self.options["opencv"].intensity_transform
        cmake.definitions["OPENCV_WITH_OPTFLOW"] = self.options["opencv"].optflow
        cmake.definitions["OPENCV_WITH_REG"] = self.options["opencv"].reg
        cmake.definitions["OPENCV_WITH_RGBD"] = self.options["opencv"].rgbd
        cmake.definitions["OPENCV_WITH_SFM"] = self.options["opencv"].sfm
        cmake.definitions["OPENCV_WITH_SHAPE"] = self.options["opencv"].shape
        cmake.definitions["OPENCV_WITH_STRUCTURED_LIGHT"] = self.options["opencv"].structured_light
        cmake.definitions["OPENCV_WITH_SURFACE_MATCHING"] = self.options["opencv"].surface_matching
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(f"ctest --output-on-failure -C {self.settings.build_type} -j {tools.cpu_count()}", run_environment=True)
