import os
import glob
from conans import ConanFile, tools, CMake


class JpegCompressorConan(ConanFile):
    name = "jpeg-compressor"
    description = "C++ JPEG compression/fuzzed low-RAM JPEG decompression codec with Public Domain or Apache 2.0 license"
    homepage = "https://github.com/richgel999/jpeg-compressor"
    topics = ("conan", "jpeg", "image", "compression", "decompression")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Public Domain", "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

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
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license(self):
        with open(os.path.join(self._source_subfolder, "jpge.cpp")) as f:
            content_lines = f.readlines()
        license_content = []
        for i in range(4, 20):
            license_content.append(content_lines[i][3:-1])
        tools.save("LICENCE.txt", "\n".join(license_content))


    def package(self):
        # self.copy("license.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        self._extract_license()
        self.copy(pattern="LICENCE.txt", dst="licenses")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
