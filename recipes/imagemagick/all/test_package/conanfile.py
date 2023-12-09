from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
            with open('delegates.txt') as f:
                content = f.read()

                def check(option, token):
                    self.output.info('checking feature %s...' % token)
                    if option:
                        if token not in content.split():
                            raise Exception("feature %s wasn't enabled!" % token)
                    self.output.info('checking feature %s... OK!' % token)

                check(self.options['imagemagick'].with_zlib, 'zlib')
                check(self.options['imagemagick'].with_bzlib, 'bzlib')
                check(self.options['imagemagick'].with_lzma, 'lzma')
                check(self.options['imagemagick'].with_lcms, 'lcms')
                check(self.options['imagemagick'].with_openexr, 'openexr')
                check(self.options['imagemagick'].with_heic, 'heic')
                check(self.options['imagemagick'].with_jbig, 'jbig')
                check(self.options['imagemagick'].with_jpeg, 'jpeg')
                check(self.options['imagemagick'].with_openjp2, 'jp2')
                check(self.options['imagemagick'].with_pango, 'pangocairo')
                check(self.options['imagemagick'].with_png, 'png')
                check(self.options['imagemagick'].with_tiff, 'tiff')
                check(self.options['imagemagick'].with_webp, 'webp')
                check(self.options['imagemagick'].with_freetype, 'freetype')
                check(self.options['imagemagick'].with_xml2, 'xml')
