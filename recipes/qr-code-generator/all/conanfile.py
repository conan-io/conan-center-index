from conan import ConanFile, tools
from conans import CMake
import os
import functools

required_conan_version = ">=1.33.0"


class QrCodeGeneratorConan(ConanFile):
    name = "qr-code-generator"
    description = "High-quality QR Code generator library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nayuki/QR-Code-generator"
    topics = ["qr-code", "qr-generator", "c-plus-plus"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

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
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
