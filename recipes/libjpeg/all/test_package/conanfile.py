from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    @property
    def _test_transupp(self):
        # transupp+libjpeg makes use of stdio of the C library. This cannot be used when using a dll libjpeg, built with a static c library.
        return not (self.options["libjpeg"].shared and self.settings.compiler == "Visual Studio" and "MT" in self.settings.compiler.runtime)

    def build_requirements(self):
        if hasattr(self, "settings_build") and tools.cross_building(self) and \
           self.settings.os == "Macos" and self.settings.arch == "armv8":
            # Workaround for CMake bug with error message:
            # Attempting to use @rpath without CMAKE_SHARED_LIBRARY_RUNTIME_C_FLAG being
            # set. This could be because you are using a Mac OS X version less than 10.5
            # or because CMake's platform configuration is corrupt.
            # FIXME: Remove once CMake on macOS/M1 CI runners is upgraded.
            self.build_requires("cmake/3.22.0")

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
