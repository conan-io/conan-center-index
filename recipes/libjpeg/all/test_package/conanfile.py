from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    @property
    def _build_transupp(self):
        # transupp+libjpeg makes use of stdio of the C library. This cannot be used when using a dll libjpeg, built with a static c library.
        return not (self.dependencies["libjpeg"].options.shared and is_msvc(self) and is_msvc_static_runtime(self))

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TRANSUPP"] = self._build_transupp
        if self._build_transupp:
            tc.variables["LIBJPEG_RES_DIR"] = self.dependencies["libjpeg"].cpp_info.resdirs[0].replace("\\", "/")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            img_name = os.path.join(self.source_folder, "testimg.jpg")
            self.run(f"{bin_path} {img_name}", env="conanrun")
            test_transupp_path = os.path.join(self.cpp.build.bindirs[0], "test_transupp")
            if os.path.exists(test_transupp_path):
                out_img = os.path.join(self.build_folder, "outimg.jpg")
                self.run(f"{test_transupp_path} {img_name} {out_img}", env="conanrun")
