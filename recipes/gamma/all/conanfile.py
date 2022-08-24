from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import functools

required_conan_version = ">=1.33.0"


class Gammaconan(ConanFile):
    name = "gamma"
    description = (
        "Gamma is a cross-platform, C++ library for doing generic synthesis "
        "and filtering of signals."
    )
    license = "MIT"
    topics = ("gamma", "signal-processing", "sound", "audio")
    homepage = "https://github.com/LancePutnam/Gamma"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "audio_io": [True, False],
        "soundfile": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "audio_io": False,
        "soundfile": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.soundfile:
            self.requires("libsndfile/1.0.31")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

        if self.options.audio_io:
            # TODO: add audio_io support once portaudio added to CCI
            raise ConanInvalidConfiguration(
                "gamma:audio_io=True requires portaudio, not available in conan-center yet"
            )

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["GAMMA_AUDIO_IO"] = self.options.audio_io
        cmake.definitions["GAMMA_SOUNDFILE"] = self.options.soundfile
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["Gamma"]
        if not self.options.shared and self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
