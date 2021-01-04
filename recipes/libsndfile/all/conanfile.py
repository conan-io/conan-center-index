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
        "programs": [True, False],
        "experimental": [True, False],
        "with_alsa": [True, False],
        "with_sqlite": ["deprecated", True, False],
        "with_external_libs": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "programs": True,
        "experimental": False,
        "with_alsa": False,
        "with_sqlite": "deprecated",
        "with_external_libs": True,

    }
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.get_safe("with_alsa"):
            self.requires("libalsa/1.2.2")
        if self.options.with_external_libs:
            self.requires("ogg/1.3.4")
            self.requires("vorbis/1.3.7")
            self.requires("flac/1.3.3")
            self.requires("opus/1.3.1")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_alsa

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.with_sqlite != "deprecated":
            self.output.warn("with_sqlite is a deprecated option. Do not use.")
        del self.options.with_sqlite

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Sndio"] = True  # FIXME: missing sndio cci recipe (check whether it is really required)
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Speex"] = True  # FIXME: missing sndio cci recipe (check whether it is really required)
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_SQLite3"] = True  # only used for regtest
        self._cmake.definitions["ENABLE_EXTERNAL_LIBS"] = self.options.with_external_libs
        if not self.options.with_external_libs:
            self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Ogg"] = True
            self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Vorbis"] = True
            self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_FLAC"] = True
            self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Opus"] = True
        if not self.options.get_safe("with_alsa", False):
            self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_ALSA"] = True
        self._cmake.definitions["BUILD_PROGRAMS"] = self.options.programs
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["ENABLE_CPACK"] = False
        self._cmake.definitions["ENABLE_EXPERIMENTAL"] = self.options.experimental
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["ENABLE_STATIC_RUNTIME"] = "MT" in str(self.settings.compiler.runtime)
        self._cmake.definitions["BUILD_REGTEST"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "SndFile"
        self.cpp_info.names["cmake_find_package"] = "SndFile"
        self.cpp_info.names["pkg_config"] = "sndfile"
        self.cpp_info.components["sndfile"].libs = ["sndfile"]
        if self.options.with_external_libs:
            self.cpp_info.components["sndfile"].requires.extend(["ogg::ogg", "vorbis::vorbis", "flac::flac", "opus::opus"])
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.components["sndfile"].system_libs = ["m", "dl", "pthread", "rt"]
            elif self.settings.os == "Windows":
                self.cpp_info.components["sndfile"].system_libs.append("winmm")
        if self.options.get_safe("with_alsa"):
            self.cpp_info.components["sndfile"].requires.append("libalsa::libalsa")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
