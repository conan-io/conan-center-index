from conans import ConanFile, tools


class VirtualjpegConan(ConanFile):
    name = "virtual-libjpeg"
    description = "Virtual package to choose jpeg encoder/decoder implementation in final package."
    url = "https://github.com/conan-io/conan-center-index"

    options = {
        "implementation": ["libjpeg", "libjpeg-turbo", "openjpeg", "mozjpeg"],
    }
    default_options = {
        "implementation": "libjpeg-turbo",
    }

    def requirements(self):
        if self.options.implementation == "libjpeg":
            self.requires("libjpeg/9d@")
        elif self.options.implementation == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.0.5@")
        elif self.options.implementation == "openjpeg":
            self.requires("openjpeg/2.3.1@")
        else: #if self.options.implementation == "mozjpeg":
            self.requires("mozjpeg/3.3.1@")
