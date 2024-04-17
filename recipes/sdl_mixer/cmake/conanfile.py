import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.57.0"


class SDLMixerConan(ConanFile):
    name = "sdl_mixer"
    description = "SDL_mixer is a sample multi-channel audio mixer library"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libsdl.org/projects/SDL_mixer/"
    topics = ("sdl2", "sdl", "mixer", "audio", "multimedia", "sound", "music")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cmd": [True, False],
        "wav": [True, False],
        "flac": [True, False],
        "gme": [True, False],
        "minimp3": [True, False],
        "mpg123": [True, False],
        "opus": [True, False],
        "modplug": [True, False],
        "fluidsynth": [True, False],
        "nativemidi": [True, False],
        "tinymidi": [True, False],
        "vorbis": [False, "vorbisfile", "tremor", "stb"],
        "wavpack": [True, False],
        "xmp": [False, "libxmp", "libxmp-lite"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cmd": False,
        "wav": True,
        "flac": True,
        "gme": False,
        "minimp3": False,
        "mpg123": True,
        "opus": True,
        "modplug": True,
        "fluidsynth": False,
        "nativemidi": True,
        "tinymidi": True,
        "vorbis": "stb",
        "wavpack": False,
        "xmp": False
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.tinymidi
        if not (self.settings.os == "Windows" or is_apple_os(self)):
            del self.options.nativemidi

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if not self.options.flac and self.options.gme:
            raise ConanInvalidConfiguration("gme is not yet available in CCI, contributions are welcome")
        if self.options.vorbis == "tremor":
            raise ConanInvalidConfiguration("tremor is not yet available in CCI, contributions are welcome")
        if self.options.xmp == "libxmp":
            raise ConanInvalidConfiguration("libxmp is not yet available in CCI, contributions are welcome")
        if self.options.xmp == "libxmp-lite":
            raise ConanInvalidConfiguration("libxmp-lite is not yet available in CCI, contributions are welcome")
        if self.options.fluidsynth:
            raise ConanInvalidConfiguration("fluidsynth is not yet available in CCI, contributions are welcome")
        if self.options.wavpack:
            raise ConanInvalidConfiguration("wavpack is not yet available in CCI, contributions are welcome")

    def requirements(self):
        self.requires("sdl/2.28.5", transitive_headers=True, transitive_libs=True)
        if self.options.flac:
            self.requires("flac/1.4.2")
        elif self.options.gme:
            # TODO: not available on CCI
            # self.requires("gme/x.y.z")
            pass
        if self.options.mpg123:
            self.requires("mpg123/1.31.2")
        if self.options.minimp3:
            self.requires("minimp3/cci.20211201")
        if self.options.vorbis == "stb":
            self.requires("stb/cci.20230920")
        elif self.options.vorbis == "vorbisfile":
            self.requires("vorbis/1.3.7")
        elif self.options.vorbis == "tremor":
            # TODO: not available on CCI
            # self.requires("tremor/1.2.1")
            pass
        if self.options.opus:
            self.requires("opusfile/0.12")
        if self.options.modplug:
            self.requires("libmodplug/0.8.9.0")
        if self.options.xmp == "libxmp":
            # TODO: not available on CCI
            # self.requires("libxmp/x.y.z")
            pass
        elif self.options.xmp == "libxmp-lite":
            # TODO: not available on CCI
            # self.requires("libxmp-lite/x.y.z")
            pass
        if self.options.fluidsynth:
            # TODO: not available on CCI
            # self.requires("fluidsynth/2.2")
            pass
        if self.options.get_safe("tinymidi"):
            self.requires("tinymidi/cci.20130325")
        # https://github.com/libsdl-org/SDL_mixer/blob/release-2.6.3/CMakeLists.txt#L148-L162
        if self.options.vorbis or self.options.flac or self.options.opus:
            self.requires("ogg/1.3.5")
        if self.options.wavpack:
            # TODO: not available on CCI
            # self.requires("wavpack/x.y.z")
            pass

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        rmdir(self, os.path.join(self.source_folder, "external"))

    def generate(self):
        tc = CMakeToolchain(self)
        # Disable debug postfix as it's not relevant to single-configuration Conan builds
        # and will be removed in v3.0 anyway.
        tc.variables["SDL2MIXER_DEBUG_POSTFIX"] = ""
        tc.variables["SDL2MIXER_VENDORED"] = False
        tc.variables["SDL2MIXER_SAMPLES"] = False
        tc.variables["SDL2MIXER_CMD"] = self.options.cmd
        # WAVE
        tc.variables["SDL2MIXER_WAVE"] = self.options.wav
        # FLAC
        tc.variables["SDL2MIXER_FLAC"] = self.options.flac
        # GME
        tc.variables["SDL2MIXER_GME"] = self.options.gme
        # MOD
        tc.variables["SDL2MIXER_MOD"] = self.options.modplug or bool(self.options.xmp)
        tc.variables["SDL2MIXER_MOD_MODPLUG"] = self.options.modplug
        tc.variables["SDL2MIXER_MOD_XMP"] = self.options.xmp == "libxmp"
        tc.variables["SDL2MIXER_MOD_XMP_LITE"] = self.options.xmp == "libxmp-lite"
        # MP3
        tc.variables["SDL2MIXER_MP3"] = self.options.mpg123 or self.options.minimp3
        tc.variables["SDL2MIXER_MP3_MPG123"] = self.options.mpg123
        tc.variables["SDL2MIXER_MP3_MINIMP3"] = self.options.minimp3
        # MIDI
        tc.variables["SDL2MIXER_MIDI"] = self.options.get_safe("nativemidi", False) or self.options.get_safe("tinymidi", False) or self.options.fluidsynth
        tc.variables["SDL2MIXER_MIDI_FLUIDSYNTH"] = self.options.fluidsynth
        tc.variables["SDL2MIXER_MIDI_TIMIDITY"] = self.options.get_safe("tinymidi", False)
        tc.variables["SDL2MIXER_MIDI_NATIVE"] = self.options.get_safe("nativemidi", False)
        # OPUS
        tc.variables["SDL2MIXER_OPUS"] = self.options.opus
        # VORBIS
        if self.options.vorbis == "stb":
            tc.variables["SDL2MIXER_VORBIS"] = "STB"
        elif self.options.vorbis == "vorbisfile":
            tc.variables["SDL2MIXER_VORBIS"] = "VORBISFILE"
        elif self.options.vorbis == "tremor":
            tc.variables["SDL2MIXER_VORBIS"] = "TREMOR"
        else:
            tc.variables["SDL2MIXER_VORBIS"] = False
        # WavPack
        tc.variables["SDL2MIXER_WAVPACK"] = self.options.wavpack

        # TODO: add support for dynamic loading of dependencies
        tc.variables["SDL2MIXER_DEPS_SHARED"] = False
        tc.variables["SDL2MIXER_FLAC_LIBFLAC_SHARED"] = False
        tc.variables["SDL2MIXER_GME_SHARED"] = False
        tc.variables["SDL2MIXER_MIDI_FLUIDSYNTH_SHARED"] = False
        tc.variables["SDL2MIXER_MIDI_TIMIDITY_SHARED"] = False
        tc.variables["SDL2MIXER_MOD_MODPLUG_SHARED"] = False
        tc.variables["SDL2MIXER_MOD_XMP_SHARED"] = False
        tc.variables["SDL2MIXER_MP3_MPG123_SHARED"] = False
        tc.variables["SDL2MIXER_OGG_SHARED"] = False
        tc.variables["SDL2MIXER_OPUS_SHARED"] = False
        tc.variables["SDL2MIXER_SNDFILE_SHARED"] = False
        tc.variables["SDL2MIXER_VORBIS_TREMOR_SHARED"] = False
        tc.variables["SDL2MIXER_VORBIS_VORBISFILE_SHARED"] = False
        tc.variables["SDL2MIXER_WAVPACK_SHARED"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("flac", "cmake_file_name", "FLAC")
        deps.set_property("flac", "cmake_target_name", "FLAC::FLAC")
        deps.set_property("fluidsynth", "cmake_file_name", "FluidSynth")
        deps.set_property("fluidsynth", "cmake_target_name", "FluidSynth::libfluidsynth")
        deps.set_property("gme", "cmake_file_name", "gme")
        deps.set_property("gme", "cmake_target_name", "gme::gme")
        deps.set_property("libxmp", "cmake_file_name", "libxmp")
        deps.set_property("libxmp", "cmake_target_name", "libxmp::libxmp")
        deps.set_property("libxmp-lite", "cmake_file_name", "libxmp-lite")
        deps.set_property("libxmp-lite", "cmake_target_name", "libxmp-lite::libxmp-lite")
        deps.set_property("libmodplug", "cmake_file_name", "modplug")
        deps.set_property("libmodplug", "cmake_target_name", "modplug::modplug")
        deps.set_property("mpg123", "cmake_file_name", "mpg123")
        deps.set_property("mpg123", "cmake_target_name", "MPG123::libmpg123")
        deps.set_property("opusfile", "cmake_file_name", "OpusFile")
        deps.set_property("opusfile", "cmake_target_name", "OpusFile::opusfile")
        deps.set_property("tremor", "cmake_file_name", "tremor")
        deps.set_property("tremor", "cmake_target_name", "tremor::tremor")
        deps.set_property("vorbis", "cmake_file_name", "Vorbis")
        deps.set_property("vorbis::vorbisfile", "cmake_target_name", "Vorbis::vorbisfile")
        deps.set_property("wavpack", "cmake_file_name", "wavpack")
        deps.set_property("wavpack", "cmake_target_name", "WavPack::WavPack")

        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SDL2_mixer")
        self.cpp_info.set_property("cmake_target_name", "SDL2_mixer::SDL2_mixer")
        # https://github.com/libsdl-org/SDL_mixer/blob/release-2.6.3/CMakeLists.txt#L164-L172
        if not self.options.shared:
            self.cpp_info.set_property("cmake_target_aliases", ["SDL2_mixer::SDL2_mixer-static"])
        # The project only creates a pkg-config file for a shared lib, but add it for static as well, unofficially
        # https://github.com/libsdl-org/SDL_mixer/blob/release-2.6.3/CMakeLists.txt#L828
        self.cpp_info.set_property("pkg_config_name", "SDL2_mixer")

        if is_msvc(self) and not self.options.shared:
            self.cpp_info.libs = ["SDL2_mixer-static"]
        else:
            self.cpp_info.libs = ["SDL2_mixer"]
        self.cpp_info.includedirs.append(os.path.join("include", "SDL2"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        if self.settings.os == "Windows":
            if self.options.nativemidi:
                self.cpp_info.system_libs.append("winmm")
        elif is_apple_os(self):
            self.cpp_info.frameworks.extend(["AudioToolbox", "AudioUnit", "CoreServices", "CoreGraphics", "CoreFoundation"])
            if self.settings.os == "Macos":
                self.cpp_info.frameworks.append("AppKit")

        self.cpp_info.names["cmake_find_package"] = "SDL2_mixer"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2_mixer"
