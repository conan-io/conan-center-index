from conans import ConanFile, tools, CMake
import os


class FlacConan(ConanFile):
    name = "flac"
    description = "Free Lossless Audio Codec"
    topics = ("conan", "flac", "codec", "audio", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/flac"
    license = "BSD"
    requires = "ogg/1.3.4"
    exports_sources = "CMakeLists.txt",
    generators = "cmake",
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_asm": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_asm": False,
    }
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        if self.options.use_asm:
            self.build_requires("nasm/2.13.02")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_ASM"] = self.options.use_asm
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING.*", dst="licenses", src=self._source_subfolder, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["FLAC__NO_DLL"]
