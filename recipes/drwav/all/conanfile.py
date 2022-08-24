from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.33.0"


class DrwavConan(ConanFile):
    name = "drwav"
    description = "WAV audio loader and writer."
    homepage = "https://mackron.github.io/dr_wav"
    topics = ("audio", "wav", "wave", "sound")
    license = ("Unlicense", "MIT-0")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False],
        "no_conversion_api": [True, False],
        "no_stdio": [True, False]
    }
    default_options = {
        "shared": False, 
        "fPIC": True,
        "no_conversion_api": False,
        "no_stdio": False
    }
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "dr_wav.c"]

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
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["NO_CONVERSION_API"] = self.options.no_conversion_api
        self._cmake.definitions["NO_STDIO"] = self.options.no_stdio
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["dr_wav"]
        if self.options.shared:
            self.cpp_info.defines.append("DRWAV_DLL")
        if self.options.no_conversion_api:
            self.cpp_info.defines.append("DR_WAV_NO_CONVERSION_API")
        if self.options.no_stdio:
            self.cpp_info.defines.append("DR_WAV_NO_STDIO")
