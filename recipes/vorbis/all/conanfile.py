from conans import ConanFile, tools, CMake
import os
import glob


class VorbisConan(ConanFile):
    name = "vorbis"
    description = "The VORBIS audio codec library"
    topics = ("conan", "vorbis", "audio", "codec")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://xiph.org/vorbis/"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = "ogg/1.3.4"
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return  "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        # if self.settings.os == "Windows":
        #     with tools.chdir(self._source_subfolder):
        #         tools.replace_in_file("vorbis.pc.in", "Libs.private: -lm", "Libs.private:")
        # elif self.settings.os == "Linux":
        #     if "LDFLAGS" in os.environ:
        #         os.environ["LDFLAGS"] = os.environ["LDFLAGS"] + " -lm"
        #     else:
        #         os.environ["LDFLAGS"] = "-lm"
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # self.cpp_info.filenames["cmake_find_package_multi"] = "Vorbis"
        # self.cpp_info.filenames["cmake_find_package_multi"] = "Vorbis"
        self.cpp_info.names["cmake_find_package"] = "Vorbis"
        self.cpp_info.names["cmake_find_package_multi"] = "Vorbis"

        self.cpp_info.components["libvorbis"].libs = ["vorbis"]
        self.cpp_info.components["libvorbis"].requires = ["ogg::ogg"]
        self.cpp_info.components["libvorbis"].names["pkgconfig"] = "vorbis"
        self.cpp_info.components["libvorbis"].names["cmake_find_package"] = "vorbis"
        self.cpp_info.components["libvorbis"].names["cmake_find_package_multi"] = "vorbis"

        self.cpp_info.components["libvorbisenc"].libs = ["vorbisenc"]
        self.cpp_info.components["libvorbisenc"].requires = ["libvorbis"]
        self.cpp_info.components["libvorbisenc"].names["pkgconfig"] = "vorbisenc"
        self.cpp_info.components["libvorbisenc"].names["cmake_find_package"] = "vorbisenc"
        self.cpp_info.components["libvorbisenc"].names["cmake_find_package_multi"] = "vorbisenc"

        self.cpp_info.components["libvorbisfile"].libs = ["vorbisfile"]
        self.cpp_info.components["libvorbisfile"].requires = ["libvorbis"]
        self.cpp_info.components["libvorbisfile"].names["pkgconfig"] = "vorbisfile"
        self.cpp_info.components["libvorbisfile"].names["cmake_find_package"] = "vorbisfile"
        self.cpp_info.components["libvorbisfile"].names["cmake_find_package_multi"] = "vorbisfile"

        # VorbisConfig.cmake defines components 'Enc' and 'File',
        # which create the imported targets Vorbs::vorbisenc and Vorbis::vorbisfile
        self.cpp_info.components["Enc"].requires.append("libvorbisenc")
        self.cpp_info.components["File"].requires.append("libvorbisenc")

        if self.settings.os == "Linux":
            self.cpp_info.components["libvorbis"].system_libs.append("m")
