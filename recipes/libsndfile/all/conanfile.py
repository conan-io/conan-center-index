from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class LibsndfileConan(ConanFile):
    name = "libsndfile"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.mega-nerd.com/libsndfile"
    description = (
        "Libsndfile is a library of C routines for reading and writing files "
        "containing sampled audio data."
    )
    topics = ("audio",)
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "programs": [True, False],
        "experimental": [True, False],
        "with_alsa": [True, False],
        "with_external_libs": [True, False],
        "with_mpeg": [True, False],
        "with_sndio": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "programs": True,
        "experimental": False,
        "with_alsa": False,
        "with_external_libs": True,
        "with_mpeg": True,
        "with_sndio": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_alsa
        if Version(self.version) < "1.1.0":
            del self.options.with_mpeg

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def validate(self):
        if self.options.with_sndio:
            if self.dependencies["libsndio"].options.get_safe("with_alsa") and not self.options.get_safe("with_alsa"):
                raise ConanInvalidConfiguration(f"{self.ref} 'with_alsa' option should be True when the libsndio 'with_alsa' one is True")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_sndio:
            self.requires("libsndio/1.9.0", options={"with_alsa": self.options.get_safe("with_alsa")})
        if self.options.get_safe("with_alsa"):
            self.requires("libalsa/1.2.10")
        if self.options.with_external_libs:
            self.requires("ogg/1.3.5")
            self.requires("vorbis/1.3.7")
            self.requires("flac/1.4.2")
            self.requires("opus/1.4")
        if self.options.get_safe("with_mpeg"):
            self.requires("mpg123/1.31.2")
            self.requires("libmp3lame/3.100")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_Speex"] = True  # FIXME: missing speex cci recipe (check whether it is really required)
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_SQLite3"] = True  # only used for regtest
        tc.variables["ENABLE_EXTERNAL_LIBS"] = self.options.with_external_libs
        if not self.options.with_external_libs:
            tc.variables["CMAKE_DISABLE_FIND_PACKAGE_Ogg"] = True
            tc.variables["CMAKE_DISABLE_FIND_PACKAGE_Vorbis"] = True
            tc.variables["CMAKE_DISABLE_FIND_PACKAGE_FLAC"] = True
            tc.variables["CMAKE_DISABLE_FIND_PACKAGE_Opus"] = True
        if not self.options.get_safe("with_alsa", False):
            tc.variables["CMAKE_DISABLE_FIND_PACKAGE_ALSA"] = True
        tc.variables["BUILD_PROGRAMS"] = self.options.programs
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.variables["ENABLE_CPACK"] = False
        tc.variables["ENABLE_EXPERIMENTAL"] = self.options.experimental
        if is_msvc(self) and Version(self.version) < "1.0.30":
            tc.variables["ENABLE_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.variables["BUILD_REGTEST"] = False
        # https://github.com/libsndfile/libsndfile/commit/663a59aa6ea5e24cf5159b8e1c2b0735712ea74e#diff-1e7de1ae2d059d21e1dd75d5812d5a34b0222cef273b7c3a2af62eb747f9d20a
        if Version(self.version) >= "1.1.0":
            tc.variables["ENABLE_MPEG"] = self.options.with_mpeg
        # Fix iOS/tvOS/watchOS
        tc.variables["CMAKE_MACOSX_BUNDLE"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SndFile")
        self.cpp_info.set_property("cmake_target_name", "SndFile::sndfile")
        self.cpp_info.set_property("pkg_config_name", "sndfile")
        self.cpp_info.libs = ["sndfile"]
        if self.options.with_sndio:
            self.cpp_info.requires.append("libsndio::libsndio")
        if self.options.with_external_libs:
            self.cpp_info.requires.extend([
                "ogg::ogg", "vorbis::vorbismain", "vorbis::vorbisenc",
                "flac::flac", "opus::opus",
            ])
        if self.options.get_safe("with_mpeg", False):
            self.cpp_info.requires.append("mpg123::mpg123")
            self.cpp_info.requires.append("libmp3lame::libmp3lame")
        if self.options.get_safe("with_alsa"):
            self.cpp_info.requires.append("libalsa::libalsa")
        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs = ["m", "dl", "pthread", "rt"]
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs.append("winmm")