import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.32.0"

class TinyAesCConan(ConanFile):
    name = "tiny-aes-c"
    license = "Unlicense"
    homepage = "https://github.com/kokke/tiny-AES-c"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Small portable AES128/192/256 in C"
    topics = ("encryption", "crypto", "AES")

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    _options_dict = {
        # enable AES128
        "aes128": [True, False],
        # enable AES192
        "aes192": [True, False],
        # enable AES256
        "aes256": [True, False],
        # enable AES encryption in CBC-mode of operation
        "cbc": [True, False],
        # enable the basic ECB 16-byte block algorithm
        "ecb": [True, False],
        # enable encryption in counter-mode
        "ctr": [True, False],
    }

    options.update(_options_dict)

    default_options = {
        "shared": False,
        "fPIC": True,
        "aes128": True,
        "aes192": False,
        "aes256": False,
        "cbc": True,
        "ecb": True,
        "ctr": True,
    }

    exports_sources = ["CMakeLists.txt"]
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
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def validate(self):
        if not self.options.cbc and not self.options.ecb and not self.options.ctr:
            raise ConanInvalidConfiguration("Need to at least specify one of CBC, ECB or CTR modes")

        if not self.options.aes128 and not self.options.aes192 and not self.options.aes256:
            raise ConanInvalidConfiguration("Need to at least specify one of AES{128, 192, 256} modes")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "tiny-AES-c-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        for key in self._options_dict.keys():
            if self.options[key]:
                self._cmake.definitions["CMAKE_CFLAGS"].append(key)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("unlicense.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=self._source_subfolder)
        self.copy(pattern="*.hpp", dst="include", src=self._source_subfolder)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dll", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["tiny-aes"]
