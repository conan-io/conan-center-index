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
        "with_sqlite": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "programs": True,
        "experimental": False,
        "with_alsa": False,
        "with_sqlite": True,
    }
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.get_safe("with_alsa"):
            self.requires("libalsa/1.2.2")
        if self.options.with_sqlite:
            self.requires("sqlite3/3.32.3")
        self.requires("flac/1.3.3")
        self.requires("ogg/1.3.4")
        self.requires("opus/1.3.1")
        self.requires("vorbis/1.3.7")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_alsa

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_PROGRAMS"] = self.options.programs
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["ENABLE_CPACK"] = False
        self._cmake.definitions["ENABLE_EXPERIMENTAL"] = self.options.experimental
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["ENABLE_STATIC_RUNTIME"] = "MT" in str(self.settings.compiler.runtime)
        self._cmake.definitions["BUILD_REGTEST"] = False
        self._cmake.definitions["ENABLE_EXTERNAL_LIBS"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
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
        self.cpp_info.components["sndfile"].requires = ["flac::flac", "ogg::ogg", "opus::opus", "vorbis::vorbis"]
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.components["sndfile"].system_libs = ["m", "dl", "pthread", "rt"]
            elif self.settings.os == "Windows":
                self.cpp_info.components["sndfile"].system_libs.append("winmm")
        if self.options.get_safe("with_alsa"):
            self.cpp_info.components["sndfile"].requires.append("libalsa::libalsa")
        if self.options.with_sqlite:
            self.cpp_info.components["sndfile"].requires.append("sqlite3::sqlite3")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
