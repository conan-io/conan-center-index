from conans import ConanFile, CMake, tools
import os


class LibsndfileConan(ConanFile):
    name = "libsndfile"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.mega-nerd.com/libsndfile"
    description = "Libsndfile is a library of C routines for reading and writing files containing sampled audio data."
    topics = ("audio")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_alsa": [True, False],
        "with_sqlite": [True, False],
        "with_external_libs": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_alsa": False,
        "with_sqlite": True,
        "with_external_libs": True,
    }
    generators = "cmake"

    _cmake = None

    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.with_alsa:
            self.requires("libalsa/1.1.9")
        if self.options.with_sqlite:
            self.requires("sqlite3/3.29.0")
        if self.options.with_external_libs:
            self.requires("flac/1.3.3")
            self.requires("ogg/1.3.4")
            self.requires("vorbis/1.3.6")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get("https://github.com/erikd/libsndfile/archive/v{0}.tar.gz".format(self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder())

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["BUILD_REGTEST"] = self.options.with_sqlite
        self._cmake.definitions["ENABLE_EXTERNAL_LIBS"] = self.options.with_external_libs
        self._cmake.configure(source_folder=self._source_subfolder())
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder())
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["sndfile"]
