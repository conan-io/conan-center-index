from conan import ConanFile
from conans import CMake
from conan import ConanFile
from conan.tools.files import get, rmdir
import os
import functools


class SDLMixerConan(ConanFile):
    name = "sdl_mixer"
    description = "SDL_mixer is a sample multi-channel audio mixer library"
    topics = ("sdl_mixer", "sdl2", "sdl", "mixer", "audio", "multimedia", "sound", "music")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libsdl.org/projects/SDL_mixer/"
    license = "Zlib"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package_multi"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "cmd": [True, False],
               "wav": [True, False],
               "flac": [True, False],
               "mpg123": [True, False],
               "mad": [True, False],
               "ogg": [True, False],
               "opus": [True, False],
               "mikmod": [True, False],
               "modplug": [True, False],
               "fluidsynth": [True, False],
               "nativemidi": [True, False],
               "tinymidi": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "cmd": False,  # needs sys/wait.h
                       "wav": True,
                       "flac": True,
                       "mpg123": True,
                       "mad": True,
                       "ogg": True,
                       "opus": True,
                       "mikmod": True,
                       "modplug": True,
                       "fluidsynth": False, # TODO: add fluidsynth to Conan Center
                       "nativemidi": True,
                       "tinymidi": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.tinymidi
        else:
            del self.options.nativemidi

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("sdl/2.0.20")
        if self.options.flac:
            self.requires("flac/1.3.3")
        if self.options.mpg123:
            self.requires("mpg123/1.29.3")
        if self.options.mad:
            self.requires("libmad/0.15.1b")
        if self.options.ogg:
            self.requires("ogg/1.3.5")
            self.requires("vorbis/1.3.7")
        if self.options.opus:
            self.requires("openssl/1.1.1q")
            self.requires("opus/1.3.1")
            self.requires("opusfile/0.12")
        if self.options.mikmod:
            self.requires("libmikmod/3.3.11.1")
        if self.options.modplug:
            self.requires("libmodplug/0.8.9.0")
        if self.options.fluidsynth:
            self.requires("fluidsynth/2.2") # TODO: this package is missing on the conan-center-index
        if self.settings.os == "Linux":
            if self.options.tinymidi:
                self.requires("tinymidi/cci.20130325")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

        rmdir(self, os.path.join(self._source_subfolder, "external"))

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMD"] = self.options.cmd
        cmake.definitions["WAV"] = self.options.wav
        cmake.definitions["FLAC"] = self.options.flac
        cmake.definitions["MP3_MPG123"] = self.options.mpg123
        cmake.definitions["MP3_MAD"] = self.options.mad
        cmake.definitions["OGG"] = self.options.ogg
        cmake.definitions["OPUS"] = self.options.opus
        cmake.definitions["MOD_MIKMOD"] = self.options.mikmod
        cmake.definitions["MOD_MODPLUG"] = self.options.modplug
        cmake.definitions["MID_FLUIDSYNTH"] = self.options.fluidsynth
        if self.settings.os == "Linux":
            cmake.definitions["MID_TINYMIDI"] = self.options.tinymidi
            cmake.definitions["MID_NATIVE"] = False
        else:
            cmake.definitions["MID_TINYMIDI"] = False
            cmake.definitions["MID_NATIVE"] = self.options.nativemidi

        cmake.definitions["FLAC_DYNAMIC"] = self.options["flac"].shared if self.options.flac else False
        cmake.definitions["MP3_MPG123_DYNAMIC"] = self.options["mpg123"].shared if self.options.mpg123 else False
        cmake.definitions["OGG_DYNAMIC"] = self.options["ogg"].shared if self.options.ogg else False
        cmake.definitions["OPUS_DYNAMIC"] = self.options["opus"].shared if self.options.opus else False
        cmake.definitions["MOD_MIKMOD_DYNAMIC"] = self.options["libmikmod"].shared if self.options.mikmod else False
        cmake.definitions["MOD_MODPLUG_DYNAMIC"] = self.options["libmodplug"].shared if self.options.modplug else False

        cmake.configure(build_folder=self._build_subfolder)

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "SDL2_mixer")
        self.cpp_info.set_property("cmake_file_name", "SDL2_mixer")
        self.cpp_info.set_property("cmake_target_name", "SDL2_mixer::SDL2_mixer")
        self.cpp_info.set_property("pkg_config_name", "SDL2_mixer")
        self.cpp_info.libs = ["SDL2_mixer"]
        self.cpp_info.includedirs.append(os.path.join("include", "SDL2"))

        self.cpp_info.names["cmake_find_package"] = "SDL2_mixer"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2_mixer"
