import os

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            return

        bin_path = os.path.join(self.cpp.build.bindir, "test_package")
        self.run(bin_path, env="conanrun")

        options = self.dependencies["imagemagick"].options
        with open("delegates.txt") as f:
            content = f.read()

        def check(option, token):
            self.output.info("checking feature %s..." % token)
            if option and token not in content.split():
                raise ConanException("feature %s wasn't enabled!" % token)
            self.output.info("checking feature %s... OK!" % token)

        check(options.with_zlib, "zlib")
        check(options.with_bzlib, "bzlib")
        check(options.with_lzma, "lzma")
        check(options.with_lcms, "lcms")
        check(options.with_openexr, "openexr")
        check(options.with_heic, "heic")
        check(options.with_jbig, "jbig")
        check(options.with_jpeg, "jpeg")
        check(options.with_openjp2, "jp2")
        check(options.with_pango, "pangocairo")
        check(options.with_png, "png")
        check(options.with_tiff, "tiff")
        check(options.with_webp, "webp")
        check(options.with_freetype, "freetype")
        check(options.with_xml2, "xml")
