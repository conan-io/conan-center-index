from conans import ConanFile, tools


class VirtualjpegConan(ConanFile):
    name = "virtual-libjpeg"
    description = "Virtual package to choose jpeg encoder/decoder implementation in final package."
    url = "https://github.com/conan-io/conan-center-index"

    options = {
        "provider": ["libjpeg", "libjpeg-turbo", "mozjpeg"],
    }
    default_options = {
        "provider": "libjpeg-turbo",
    }

    def requirements(self):
        if self.options.provider == "libjpeg":
            self.requires("libjpeg/9d@")
        elif self.options.provider == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.0.5@")
        else: #if self.options.provider == "mozjpeg":
            self.requires("mozjpeg/3.3.1@")
