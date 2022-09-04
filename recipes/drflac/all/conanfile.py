from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class DrflacConan(ConanFile):
    name = "drflac"
    description = "FLAC audio decoder."
    homepage = "https://mackron.github.io/dr_flac"
    topics = ("audio", "flac", "sound")
    license = ("Unlicense", "MIT-0")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False],
        "buffer_size": "ANY",
        "no_crc": [True, False],
        "no_ogg": [True, False],
        "no_simd": [True, False],
        "no_stdio": [True, False]
    }
    default_options = {
        "shared": False, 
        "fPIC": True,
        "buffer_size": 0, # zero means the default buffer size is used
        "no_crc": False,
        "no_ogg": False,
        "no_simd": False,
        "no_stdio": False
    }
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "dr_flac.c"]

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
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUFFER_SIZE"] = self.options.buffer_size
        self._cmake.definitions["NO_CRC"] = self.options.no_crc
        self._cmake.definitions["NO_OGG"] = self.options.no_ogg
        self._cmake.definitions["NO_SIMD"] = self.options.no_simd
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
        self.cpp_info.libs = ["dr_flac"]
        if self.options.shared:
            self.cpp_info.defines.append("DRFLAC_DLL")
        if self.options.buffer_size != "0":
            self.cpp_info.defines.append("DR_FLAC_BUFFER_SIZE={}".format(self.options.buffer_size))
        if self.options.no_crc:
            self.cpp_info.defines.append("DR_FLAC_NO_CRC")
        if self.options.no_ogg:
            self.cpp_info.defines.append("DR_FLAC_NO_OGG")
        if self.options.no_simd:
            self.cpp_info.defines.append("DR_FLAC_NO_SIMD")
        if self.options.no_stdio:
            self.cpp_info.defines.append("DR_FLAC_NO_STDIO")
