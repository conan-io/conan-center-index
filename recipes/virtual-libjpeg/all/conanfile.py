from conans import ConanFile, tools


class VirtualjpegConan(ConanFile):
    name = "virtual-libjpeg"
    description = "Virtual package to choose jpeg encoder/decoder implementation in final package."
    url = "https://github.com/conan-io/conan-center-index"

    options = {
        "implementation": ["libjpeg", "libjpeg-turbo"],
    }
    default_options = {
        "implementation": "libjpeg-turbo",
    }

    def requirements(self):
        if self.options.implementation == "libjpeg":
            self.requires("libjpeg/9d")
        else: #if self.options.implementation == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.0.5")
