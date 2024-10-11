from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class RtMidiConan(ConanFile):
    name = "rtmidi"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.music.mcgill.ca/~gary/rtmidi/"
    description = "Realtime MIDI input/output"
    topics = ("midi",)
    license = "MIT+send-patches-upstream"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _with_alsa(self):
        return self.settings.os == "Linux"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self._with_alsa:
            self.requires("libalsa/1.2.10")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.24 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["RTMIDI_BUILD_TESTING"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if Version(self.version) < "6.0.0":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "${ALSA_LIBRARY}", "ALSA::ALSA")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if Version(self.version) < "5.0.0":
            os.makedirs(os.path.join(self.package_folder, "include", "rtmidi"))
            os.rename(
                os.path.join(self.package_folder, "include", "RtMidi.h"),
                os.path.join(self.package_folder, "include", "rtmidi", "RtMidi.h"),
            )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "RtMidi")
        self.cpp_info.set_property("cmake_target_name", "RtMidi::rtmidi")
        self.cpp_info.set_property("pkg_config_name", "rtmidi")
        # TODO: back to global scope in conan v2
        self.cpp_info.components["librtmidi"].includedirs = [os.path.join("include", "rtmidi")]
        self.cpp_info.components["librtmidi"].libs = ["rtmidi"]
        if is_apple_os(self):
            self.cpp_info.components["librtmidi"].frameworks.extend(
                ["CoreFoundation", "CoreAudio", "CoreMIDI", "CoreServices"]
            )
        elif self.settings.os == "Windows":
            self.cpp_info.components["librtmidi"].system_libs.append("winmm")
        elif self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["librtmidi"].system_libs.append("pthread")

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "RtMidi"
        self.cpp_info.names["cmake_find_package_multi"] = "RtMidi"
        self.cpp_info.components["librtmidi"].names["cmake_find_package"] = "rtmidi"
        self.cpp_info.components["librtmidi"].names["cmake_find_package_multi"] = "rtmidi"
        self.cpp_info.components["librtmidi"].set_property("cmake_target_name", "RtMidi::rtmidi")
        self.cpp_info.components["librtmidi"].set_property("pkg_config_name", "rtmidi")
        if self._with_alsa:
            self.cpp_info.components["librtmidi"].requires.append("libalsa::libalsa")
