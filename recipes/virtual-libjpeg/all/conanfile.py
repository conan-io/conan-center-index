from conan import ConanFile

required_conan_version = ">=1.52.0"


class VirtualLibjpegConan(ConanFile):
    name = "virtual-libjpeg"
    description = "Proxy recipe to select either libjpeg, libjpeg-turbo or mozjpeg"
    license = "MIT"
    topics = ("proxy", "virtual", "jpeg", "libjpeg", "libjpeg-turbo", "mozjepg")
    homepage = "https://github.com/conan-io/conan-center-index"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "implementation": ["libjpeg", "libjpeg-turbo", "mozjpeg"],
    }
    default_options = {
        "implementation": "libjpeg-turbo",
    }

    @property
    def _impl_version(self):
        return {
            "libjpeg": "9e",
            "libjpeg-turbo": "2.1.4",
            "mozjpeg": "4.1.1",
        }[str(self.options.implementation)]

    def layout(self):
        pass

    def requirements(self):
        self.requires(f"{self.options.implementation}/{self._impl_version}", transitive_headers=True, transitive_libs=True)

    def package_id(self):
        self.info.clear()

    def source(self):
        pass

    def build(self):
        pass

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        if self.options.implementation == "libjpeg":
            self.cpp_info.requires = ["libjpeg::libjpeg"]
        elif self.options.implementation == "libjpeg-turbo":
            self.cpp_info.requires = ["libjpeg-turbo::jpeg"]
        elif self.options.implementation == "mozjpeg":
            self.cpp_info.requires = ["mozjpeg::libjpeg"]
