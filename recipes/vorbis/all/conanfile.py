from conans import ConanFile, tools, CMake
import os

required_conan_version = ">=1.33.0"


class VorbisConan(ConanFile):
    name = "vorbis"
    description = "The VORBIS audio codec library"
    topics = ("conan", "vorbis", "audio", "codec")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://xiph.org/vorbis/"
    license = "BSD-3-Clause"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("ogg/1.3.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
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
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Vorbis"
        self.cpp_info.names["cmake_find_package_multi"] = "Vorbis"
        self.cpp_info.names["pkg_config"] = "vorbis_full_package" # see https://github.com/conan-io/conan-center-index/pull/4173
        # vorbis
        self.cpp_info.components["vorbismain"].names["cmake_find_package"] = "vorbis"
        self.cpp_info.components["vorbismain"].names["cmake_find_package_multi"] = "vorbis"
        self.cpp_info.components["vorbismain"].names["pkg_config"] = "vorbis"
        self.cpp_info.components["vorbismain"].libs = ["vorbis"]
        if self.settings.os == "Linux":
            self.cpp_info.components["vorbismain"].system_libs.append("m")
        self.cpp_info.components["vorbismain"].requires = ["ogg::ogg"]
        # vorbisenc
        self.cpp_info.components["vorbisenc"].names["cmake_find_package"] = "vorbisenc"
        self.cpp_info.components["vorbisenc"].names["cmake_find_package_multi"] = "vorbisenc"
        self.cpp_info.components["vorbisenc"].names["pkg_config"] = "vorbisenc"
        self.cpp_info.components["vorbisenc"].libs = ["vorbisenc"]
        self.cpp_info.components["vorbisenc"].requires = ["vorbismain"]
        # vorbisfile
        self.cpp_info.components["vorbisfile"].names["cmake_find_package"] = "vorbisfile"
        self.cpp_info.components["vorbisfile"].names["cmake_find_package_multi"] = "vorbisfile"
        self.cpp_info.components["vorbisfile"].names["pkg_config"] = "vorbisfile"
        self.cpp_info.components["vorbisfile"].libs = ["vorbisfile"]
        self.cpp_info.components["vorbisfile"].requires = ["vorbismain"]

        # VorbisConfig.cmake defines components 'Enc' and 'File',
        # which create the imported targets Vorbis::vorbisenc and Vorbis::vorbisfile
        self.cpp_info.components["vorbisenc-alias"].names["cmake_find_package"] = "Enc"
        self.cpp_info.components["vorbisenc-alias"].names["cmake_find_package_multi"] = "Enc"
        self.cpp_info.components["vorbisenc-alias"].requires.append("vorbisenc")
        self.cpp_info.components["vorbisfile-alias"].names["cmake_find_package"] = "File"
        self.cpp_info.components["vorbisfile-alias"].names["cmake_find_package_multi"] = "File"
        self.cpp_info.components["vorbisfile-alias"].requires.append("vorbisfile")
