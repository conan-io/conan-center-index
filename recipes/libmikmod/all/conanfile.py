from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, replace_in_file, rmdir
import os

required_conan_version = ">=1.53.0"


class LibmikmodConan(ConanFile):
    name = "libmikmod"
    description = "Module player and library supporting many formats, including mod, s3m, it, and xm."
    topics = ("audio",)
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mikmod.sourceforge.net"
    license = "LGPL-2.1-or-later"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_dsound": [True, False],
        "with_mmsound": [True, False],
        "with_alsa": [True, False],
        "with_oss": [True, False],
        "with_pulse": [True, False],
        "with_coreaudio": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_dsound": True,
        "with_mmsound": True,
        "with_alsa": True,
        "with_oss": True,
        "with_pulse": True,
        "with_coreaudio": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.with_dsound
            del self.options.with_mmsound
        if self.settings.os != "Linux":
            del self.options.with_alsa
        # Non-Apple Unices
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_oss
            del self.options.with_pulse
        # Apple
        if is_apple_os(self):
            del self.options.with_coreaudio

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os == "Linux":
            if self.options.with_alsa:
                self.requires("libalsa/1.2.7.2")
            if self.options.with_pulse:
                self.requires("pulseaudio/14.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_STATIC"] = not self.options.shared
        tc.variables["ENABLE_DOC"] = False
        tc.variables["ENABLE_DSOUND"] = self.options.get_safe("with_dsound", False)
        tc.variables["ENABLE_MMSOUND"] = self.options.get_safe("with_mmsound", False)
        tc.variables["ENABLE_ALSA"] = self.options.get_safe("with_alsa", False)
        tc.variables["ENABLE_OSS"] = self.options.get_safe("with_oss", False)
        tc.variables["ENABLE_PULSE"] = self.options.get_safe("with_pulse", False)
        tc.variables["ENABLE_COREAUDIO"] = self.options.get_safe("with_coreaudio", False)
        # Relocatable shared libs on macOS
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

         # Ensure missing dependencies yields errors
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                              "MESSAGE(WARNING",
                              "MESSAGE(FATAL_ERROR")

        replace_in_file(self, os.path.join(self.source_folder, "drivers", "drv_alsa.c"),
                              "alsa_pcm_close(pcm_h);",
                              "if (pcm_h) alsa_pcm_close(pcm_h);")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING.LESSER", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if self.settings.os == "Windows" and self.options.shared:
            os.remove(os.path.join(self.package_folder, "bin", "libmikmod-config"))
        else:
            rmdir(self, os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libmikmod")
        self.cpp_info.libs = collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["MIKMOD_STATIC"]

        if self.options.get_safe("with_dsound"):
            self.cpp_info.system_libs.append("dsound")
        if self.options.get_safe("with_mmsound"):
            self.cpp_info.system_libs.append("winmm")
        if self.options.get_safe("with_coreaudio"):
            self.cpp_info.frameworks.append("CoreAudio")
