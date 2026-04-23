from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os


required_conan_version = ">=2.4"


class SDLMixerConan(ConanFile):
    name = "sdl_mixer"
    description = (
        "SDL_mixer decodes popular audio formats and mixes streams for SDL3 "
        "(track-based API, effects, optional codecs)."
    )
    license = "Zlib"
    topics = ("sdl3", "sdl3_mixer", "sdl", "audio", "mixer", "multimedia")
    homepage = "https://github.com/libsdl-org/SDL_mixer"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_flac": [False, "flac", "drflac"],
        "with_opus": [True, False],
        "with_vorbis": [False, "stb", "vorbisfile"],
        "with_mpg123": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_flac": "flac",
        "with_opus": True,
        "with_vorbis": "stb",
        "with_mpg123": True,
    }
    implements = ["auto_shared_fpic"]
    languages = "C"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("sdl/[>=3.4.0 <4]", transitive_headers=True)
        if self.options.with_flac == "flac":
            self.requires("flac/[>=1.4.2 <2]", transitive_headers=True, transitive_libs=True)
        if self.options.with_opus:
            self.requires("opusfile/[>=0.12 <1]", transitive_headers=True, transitive_libs=True)
        if self.options.with_vorbis == "vorbisfile":
            self.requires("vorbis/[>=1.3.7 <2]", transitive_headers=True, transitive_libs=True)
        if self.options.with_mpg123:
            self.requires("mpg123/[>=1.31.2 <2]", transitive_headers=True, transitive_libs=True)
        if self.options.with_opus or self.options.with_flac == "flac" or self.options.with_vorbis in ("stb", "vorbisfile"):
            self.requires("ogg/1.3.5", transitive_headers=True)

    def validate(self):
        if self.options.shared != self.dependencies["sdl"].options.shared:
            raise ConanInvalidConfiguration("sdl and sdl_mixer must use the same 'shared' option value")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        rmdir(self, os.path.join(self.source_folder, "external"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SDLMIXER_VENDORED"] = False
        tc.cache_variables["SDLMIXER_DEPS_SHARED"] = False
        tc.cache_variables["SDLMIXER_STRICT"] = True
        tc.cache_variables["SDLMIXER_TESTS"] = False
        tc.cache_variables["SDLMIXER_EXAMPLES"] = False
        wf = self.options.with_flac
        tc.cache_variables["SDLMIXER_FLAC"] = wf is not False
        tc.cache_variables["SDLMIXER_FLAC_LIBFLAC"] = wf == "flac"
        tc.cache_variables["SDLMIXER_FLAC_DRFLAC"] = wf == "drflac"
        tc.cache_variables["SDLMIXER_GME"] = False
        tc.cache_variables["SDLMIXER_MOD"] = False
        tc.cache_variables["SDLMIXER_MP3"] = True
        tc.cache_variables["SDLMIXER_MP3_MPG123"] = self.options.with_mpg123
        tc.cache_variables["SDLMIXER_MP3_DRMP3"] = True
        tc.cache_variables["SDLMIXER_MIDI"] = False
        tc.cache_variables["SDLMIXER_OPUS"] = self.options.with_opus
        vorbis = self.options.with_vorbis
        tc.cache_variables["SDLMIXER_VORBIS_STB"] = vorbis == "stb"
        tc.cache_variables["SDLMIXER_VORBIS_VORBISFILE"] = vorbis == "vorbisfile"
        tc.cache_variables["SDLMIXER_VORBIS_TREMOR"] = False
        tc.cache_variables["SDLMIXER_WAVPACK"] = False
        tc.generate()
        deps = CMakeDeps(self)
        if self.options.with_opus:
            deps.set_property("opusfile", "cmake_file_name", "OpusFile")
            deps.set_property("opusfile", "cmake_target_name", "OpusFile::opusfile")
        if self.options.with_vorbis == "vorbisfile":
            deps.set_property("vorbis", "cmake_file_name", "Vorbis")
            deps.set_property("vorbis::vorbisfile", "cmake_target_name", "Vorbis::vorbisfile")
        if self.options.with_mpg123:
            deps.set_property("mpg123", "cmake_file_name", "mpg123")
            deps.set_property("mpg123", "cmake_target_name", "MPG123::libmpg123")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        lib_suffix = ""
        if self.settings.os == "Windows" and not self.options.shared:
            lib_suffix = "-static"
        self.cpp_info.libs = [f"SDL3_mixer{lib_suffix}"]
        self.cpp_info.set_property("cmake_file_name", "SDL3_mixer")
        suffix = "-static" if not self.options.shared else ""
        self.cpp_info.set_property("cmake_target_name", f"SDL3_mixer::SDL3_mixer{suffix}")
        self.cpp_info.set_property("pkg_config_name", "sdl3-mixer")
