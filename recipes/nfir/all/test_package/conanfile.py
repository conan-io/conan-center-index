from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import download
from os import path

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        download(
                self,
                url="https://raw.githubusercontent.com/tomas-krupa/NFIR/refs/tags/0.2.0/doc/img/f_nist-logo-brand-2c_512wide.png",
                filename=path.join(self.build_folder, "image.png")
                )
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.run(path.join(self.cpp.build.bindir, "test_package"), env="conanrun")
            ext = ".exe" if self.settings.os == "Windows" else ""
            self.run(f"NFIR{ext} -a 1000 -b 500 -c image.png -d downsampled.png", env="conanrun")
