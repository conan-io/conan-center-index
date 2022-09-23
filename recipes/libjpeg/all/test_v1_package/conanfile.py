from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    @property
    def _test_transupp(self):
        # transupp+libjpeg makes use of stdio of the C library. This cannot be used when using a dll libjpeg, built with a static c library.
        return not (self.options["libjpeg"].shared and is_msvc(self) and is_msvc_static_runtime(self))

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            img_name = os.path.join(self.source_folder, os.pardir, "test_package", "testimg.jpg")
            self.run(f"{bin_path} {img_name}", run_environment=True)
            if self._test_transupp:
                test_transupp_path = os.path.join("bin", "test_transupp")
                out_img = os.path.join(self.build_folder, "outimg.jpg")
                self.run(f"{test_transupp_path} {img_name} {out_img}", run_environment=True)
