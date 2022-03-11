from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class QrCodeGeneratorConan(ConanFile):
    name = "qr-code-generator"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nayuki/QR-Code-generator"
    description = "High-quality QR Code generator library"
    topics = ["qr-code", "qr-generator", "c-plus-plus"]
    license = "MIT"
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True}
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license(self):
        header_name = ("QrCode.hpp" if tools.Version(self.version) < "1.7.0"
                       else "qrcodegen.hpp")
        header = tools.load(os.path.join(
            self._source_subfolder, "cpp", header_name))
        license_contents = header[2:header.find("*/", 1)]
        return license_contents

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"),
                   self._extract_license())

    def package_info(self):
        library_name = ("qrcodegen" if tools.Version(self.version) < "1.7.0"
                       else "qrcodegencpp")
        self.cpp_info.libs.append(library_name)
