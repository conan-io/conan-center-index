from conan import ConanFile, tools
from conans import CMake
import os


class LibmikmodConan(ConanFile):
    name = "libmikmod"
    description = "Module player and library supporting many formats, including mod, s3m, it, and xm."
    topics = ("libmikmod", "audio")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mikmod.sourceforge.net"
    license = "LGPL-2.1-or-later"
    exports_sources = ["patches/*", "CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_dsound": [True, False],
        "with_mmsound": [True, False],
        "with_alsa": [True, False],
        "with_oss": [True, False],
        "with_pulse": [True, False],
        "with_coreaudio": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_dsound": True,
        "with_mmsound": True,
        "with_alsa": True,
        "with_oss": True,
        "with_pulse": True,
        "with_coreaudio": True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    _cmake = None

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
        if tools.is_apple_os(self.settings.os):
            del self.options.with_coreaudio

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.settings.os == "Linux":
            if self.options.with_alsa:
                self.requires("libalsa/1.2.7.2")
            if self.options.with_pulse:
                self.requires("pulseaudio/14.2")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self, set_cmake_flags=True)
        self._cmake.definitions["ENABLE_STATIC"] = not self.options.shared
        self._cmake.definitions["ENABLE_DOC"] = False
        self._cmake.definitions["ENABLE_DSOUND"] = self.options.get_safe("with_dsound", False)
        self._cmake.definitions["ENABLE_MMSOUND"] = self.options.get_safe("with_mmsound", False)
        self._cmake.definitions["ENABLE_ALSA"] = self.options.get_safe("with_alsa", False)
        self._cmake.definitions["ENABLE_OSS"] = self.options.get_safe("with_oss", False)
        self._cmake.definitions["ENABLE_PULSE"] = self.options.get_safe("with_pulse", False)
        self._cmake.definitions["ENABLE_COREAUDIO"] = self.options.get_safe("with_coreaudio", False)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "CMAKE_SOURCE_DIR",
                              "PROJECT_SOURCE_DIR")

         # Ensure missing dependencies yields errors
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "MESSAGE(WARNING",
                              "MESSAGE(FATAL_ERROR")

        tools.replace_in_file(os.path.join(self._source_subfolder, "drivers", "drv_alsa.c"),
                              "alsa_pcm_close(pcm_h);",
                              "if (pcm_h) alsa_pcm_close(pcm_h);")

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING.LESSER", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        os.remove(os.path.join(self.package_folder, "bin", "libmikmod-config"))
        if not self.options.shared:
            tools.files.rmdir(self, os.path.join(self.package_folder, "bin"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["MIKMOD_STATIC"]
        self.cpp_info.filenames["pkg_config"] = "libmikmod"

        if self.options.get_safe("with_dsound"):
            self.cpp_info.system_libs.append("dsound")
        if self.options.get_safe("with_mmsound"):
            self.cpp_info.system_libs.append("winmm")
        if self.options.get_safe("with_coreaudio"):
            self.cpp_info.frameworks.append("CoreAudio")
