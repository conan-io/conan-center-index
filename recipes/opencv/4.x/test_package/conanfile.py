from conan import ConanFile
from conan.tools.build import build_jobs, can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import chdir


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OPENCV_WITH_CALIB3D"] = self.dependencies["opencv"].options.calib3d
        tc.variables["OPENCV_WITH_FEATURES2D"] = self.dependencies["opencv"].options.features2d
        tc.variables["OPENCV_WITH_FLANN"] = self.dependencies["opencv"].options.flann
        tc.variables["OPENCV_WITH_GAPI"] = self.dependencies["opencv"].options.gapi
        tc.variables["OPENCV_WITH_HIGHGUI"] = self.dependencies["opencv"].options.highgui
        tc.variables["OPENCV_WITH_IMGCODECS"] = self.dependencies["opencv"].options.imgcodecs and self.dependencies["opencv"].options.with_png
        tc.variables["OPENCV_WITH_IMGPROC"] = self.dependencies["opencv"].options.imgproc
        tc.variables["OPENCV_WITH_ML"] = self.dependencies["opencv"].options.ml
        tc.variables["OPENCV_WITH_OBJDETECT"] = self.dependencies["opencv"].options.objdetect
        tc.variables["OPENCV_WITH_PHOTO"] = self.dependencies["opencv"].options.photo
        tc.variables["OPENCV_WITH_STITCHING"] = self.dependencies["opencv"].options.stitching
        tc.variables["OPENCV_WITH_VIDEO"] = self.dependencies["opencv"].options.video
        tc.variables["OPENCV_WITH_VIDEOIO"] = self.dependencies["opencv"].options.videoio and self.dependencies["opencv"].options.with_ffmpeg
        tc.variables["OPENCV_WITH_ALPHAMAT"] = self.dependencies["opencv"].options.get_safe("alphamat", False)
        tc.variables["OPENCV_WITH_ARUCO"] = self.dependencies["opencv"].options.aruco
        tc.variables["OPENCV_WITH_BGSEGM"] = self.dependencies["opencv"].options.bgsegm
        tc.variables["OPENCV_WITH_BIOINSPIRED"] = self.dependencies["opencv"].options.bioinspired
        tc.variables["OPENCV_WITH_CCALIB"] = self.dependencies["opencv"].options.ccalib
        tc.variables["OPENCV_WITH_DNN_SUPERRES"] = self.dependencies["opencv"].options.dnn_superres
        tc.variables["OPENCV_WITH_FACE"] = self.dependencies["opencv"].options.face
        tc.variables["OPENCV_WITH_FREETYPE"] = self.dependencies["opencv"].options.freetype
        tc.variables["OPENCV_WITH_FUZZY"] = self.dependencies["opencv"].options.fuzzy
        tc.variables["OPENCV_WITH_HFS"] = self.dependencies["opencv"].options.hfs
        tc.variables["OPENCV_WITH_IMG_HASH"] = self.dependencies["opencv"].options.img_hash
        tc.variables["OPENCV_WITH_INTENSITY_TRANSFORM"] = self.dependencies["opencv"].options.get_safe("intensity_transform", False)
        tc.variables["OPENCV_WITH_LINE_DESCRIPTOR"] = self.dependencies["opencv"].options.line_descriptor
        tc.variables["OPENCV_WITH_MCC"] = self.dependencies["opencv"].options.get_safe("mcc", False)
        tc.variables["OPENCV_WITH_OPTFLOW"] = self.dependencies["opencv"].options.optflow
        tc.variables["OPENCV_WITH_PHASE_UNWRAPPING"] = self.dependencies["opencv"].options.phase_unwrapping
        tc.variables["OPENCV_WITH_QUALITY"] = self.dependencies["opencv"].options.quality
        tc.variables["OPENCV_WITH_REG"] = self.dependencies["opencv"].options.reg
        tc.variables["OPENCV_WITH_RGBD"] = self.dependencies["opencv"].options.rgbd
        tc.variables["OPENCV_WITH_SALIENCY"] = self.dependencies["opencv"].options.saliency
        tc.variables["OPENCV_WITH_SFM"] = self.dependencies["opencv"].options.sfm
        tc.variables["OPENCV_WITH_SHAPE"] = self.dependencies["opencv"].options.shape
        tc.variables["OPENCV_WITH_STRUCTURED_LIGHT"] = self.dependencies["opencv"].options.structured_light
        tc.variables["OPENCV_WITH_SUPERRES"] = self.dependencies["opencv"].options.get_safe("superres", False)
        tc.variables["OPENCV_WITH_SURFACE_MATCHING"] = self.dependencies["opencv"].options.surface_matching
        tc.variables["OPENCV_WITH_TEXT"] = self.dependencies["opencv"].options.text
        tc.variables["OPENCV_WITH_TRACKING"] = self.dependencies["opencv"].options.tracking
        tc.variables["OPENCV_WITH_WECHAT_QRCODE"] = self.dependencies["opencv"].options.get_safe("wechat_qrcode", False)
        tc.variables["OPENCV_WITH_XFEATURES2D"] = self.dependencies["opencv"].options.xfeatures2d
        tc.variables["OPENCV_WITH_XIMGPROC"] = self.dependencies["opencv"].options.ximgproc
        tc.variables["OPENCV_WITH_XOBJDETECT"] = self.dependencies["opencv"].options.xobjdetect
        tc.variables["OPENCV_WITH_XPHOTO"] = self.dependencies["opencv"].options.xphoto
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            with chdir(self, self.build_folder):
                self.run(f"ctest --output-on-failure -C {self.settings.build_type} -j {build_jobs(self)}", env="conanrun")
