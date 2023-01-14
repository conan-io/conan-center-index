from conan import ConanFile
from conan.tools.build import can_run
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
        tc.variables["OPENCV_WITH_FLANN"] = self.dependencies["opencv"].options.flann
        tc.variables["OPENCV_WITH_GAPI"] = self.dependencies["opencv"].options.gapi
        tc.variables["OPENCV_WITH_IMGCODECS_PNG"] = self.dependencies["opencv"].options.imgcodecs and self.dependencies["opencv"].options.with_png
        tc.variables["OPENCV_WITH_IMGPROC"] = self.dependencies["opencv"].options.imgproc
        tc.variables["OPENCV_WITH_OBJDETECT"] = self.dependencies["opencv"].options.objdetect
        tc.variables["OPENCV_WITH_VIDEOIO_FFMPEG"] = self.dependencies["opencv"].options.videoio and self.dependencies["opencv"].options.with_ffmpeg
        tc.variables["OPENCV_WITH_SFM"] = self.dependencies["opencv"].options.sfm
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            with chdir(self, self.build_folder):
                self.run(f"ctest --output-on-failure -C {self.settings.build_type}", env="conanrun")
