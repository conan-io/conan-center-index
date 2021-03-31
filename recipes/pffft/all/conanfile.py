from conans import ConanFile, CMake, tools
import glob
import os


class PffftConan(ConanFile):
    name = "pffft"
    description = "PFFFT, a pretty fast Fourier Transform."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://bitbucket.org/jpommier/pffft/src/master/"
    topics = ("fft", "pffft")
    license = "BSD-like (FFTPACK license)"
    generators = "cmake"
    settings = "os", "compiler", "arch", "build_type"
    exports_sources = ["CMakeLists.txt"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_simd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_simd": False,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("jpommier-pffft-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

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

    def package_info(self):
        self.cpp_info.libs = ["pffft"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
