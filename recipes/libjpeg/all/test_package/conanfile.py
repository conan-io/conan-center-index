from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    @property
    def _test_transupp(self):
        # transupp+libjpeg makes use of stdio of the C library. This cannot be used when using a dll libjpeg, built with a static c library.
        return not (self.options["libjpeg"].shared and self.settings.compiler == "Visual Studio" and "MT" in self.settings.compiler.runtime)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self):
            return
        img_name = os.path.join(self.source_folder, "testimg.jpg")
        out_img = os.path.join(self.build_folder, "outimg.jpg")
        self.run("%s %s" % (os.path.join("bin", "test_package"), img_name), run_environment=True)
        if self._test_transupp:
            self.run("%s %s %s" % (os.path.join("bin", "test_transupp"), img_name, out_img), run_environment=True)
