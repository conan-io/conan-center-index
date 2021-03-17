import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.28.0"


class ConanPffft(ConanFile):
    name = "pffft"
    description = "PFFFT, a pretty fast Fourier Transform."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://bitbucket.org/jpommier/pffft/src/master/"
    topics = ("fft", "pffft")
    license = "BSD-like (FFTPACK license)"
    generators = "cmake"
    settings = "os", "compiler", "arch", "build_type"
    exports_sources = ["CMakeLists.txt"]
    options = {"disable_simd": [True, False]}
    default_options = {"disable_simd": False}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        archive_name = os.path.basename(url)
        archive_name = "jpommier-pffft-" + os.path.splitext(archive_name)[0]
        os.rename(archive_name, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DISABLE_SIMD"] = self.options.disable_simd
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        header = tools.load(os.path.join(self._source_subfolder, "pffft.h"))
        license_content = header[: header.find("*/", 1)]
        tools.save(
            os.path.join(self.package_folder, "licenses", "LICENSE"), license_content
        )
        cmake = self._configure_cmake()
        cmake.install()
