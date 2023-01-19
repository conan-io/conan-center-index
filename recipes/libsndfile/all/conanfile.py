from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class LibsndfileConan(ConanFile):
    name = "libsndfile"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.mega-nerd.com/libsndfile"
    description = (
        "Libsndfile is a library of C routines for reading and writing files "
        "containing sampled audio data."
    )
    topics = ("audio")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "programs": [True, False],
        "experimental": [True, False],
        "with_alsa": [True, False],
        "with_external_libs": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "programs": True,
        "experimental": False,
        "with_alsa": False,
        "with_external_libs": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_alsa

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.get_safe("with_alsa"):
            self.requires("libalsa/1.2.7.2")
        if self.options.with_external_libs:
            self.requires("ogg/1.3.5")
            self.requires("vorbis/1.3.7")
            self.requires("flac/1.3.3")
            self.requires("opus/1.3.1")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_Sndio"] = True  # FIXME: missing sndio cci recipe (check whether it is really required)
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_Speex"] = True  # FIXME: missing sndio cci recipe (check whether it is really required)
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
        # Fix iOS/tvOS/watchOS
        tc.variables["CMAKE_MACOSX_BUNDLE"] = False
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
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
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["sndfile"].libs = ["sndfile"]
        if self.options.with_external_libs:
            self.cpp_info.components["sndfile"].requires.extend([
                "ogg::ogg", "vorbis::vorbismain", "vorbis::vorbisenc",
                "flac::flac", "opus::opus",
            ])
        if self.options.get_safe("with_alsa"):
            self.cpp_info.components["sndfile"].requires.append("libalsa::libalsa")
        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["sndfile"].system_libs = ["m", "dl", "pthread", "rt"]
            elif self.settings.os == "Windows":
                self.cpp_info.components["sndfile"].system_libs.append("winmm")

        if self.options.programs:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "SndFile"
        self.cpp_info.names["cmake_find_package_multi"] = "SndFile"
        self.cpp_info.components["sndfile"].set_property("cmake_target_name", "SndFile::sndfile")
