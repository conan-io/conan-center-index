from conans import ConanFile, tools


class VirtualjpegConan(ConanFile):
    name = "virtual-libjpeg"
    description = "Virtual package to choose jpeg encoder/decoder implementation in final package."
    url = "https://github.com/conan-io/conan-center-index"
    options = {"implementation": "ANY"}
    default_options = {"implementation": "libjpeg-turbo/2.0.5"}

    def requirements(self):
        self.requires(str(self.options.implementation))
