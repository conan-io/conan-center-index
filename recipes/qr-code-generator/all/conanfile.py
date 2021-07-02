from conans import ConanFile, CMake, tools
import os


class QrCodeGeneratorConan(ConanFile):
    name = "qr-code-generator"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nayuki/QR-Code-generator"
    description = "High-quality QR Code generator library in Java, JavaScript, Python, C++, C, Rust, TypeScript."
    topics = ["qr-code", "qr-generator", "c-plus-plus"]
    license = "MIT"
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {'shared': False,
                       'fPIC': True}
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("QR-Code-generator-{}".format(self.version),
                  self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license(self):
        header = tools.load(os.path.join(
            self._source_subfolder, "cpp", "QrCode.hpp"))
        license_contents = header[2:header.find("*/", 1)]
        tools.save("LICENSE", license_contents)

    def package(self):
        self._extract_license()
        self.copy("LICENSE", dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs.append("qrcodegen")
