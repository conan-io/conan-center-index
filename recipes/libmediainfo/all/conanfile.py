import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class LibmediainfoConan(ConanFile):
    name = "libmediainfo"
    license = ("BSD-2-Clause", "Apache-2.0", "GLPL-2.1+", "GPL-2.0-or-later", "MPL-2.0")
    homepage = "https://mediaarea.net/en/MediaInfo"
    url = "https://github.com/conan-io/conan-center-index"
    description = "MediaInfo is a convenient unified display of the most relevant technical and tag data for video and audio files"
    topics = ("conan", "libmediainfo", "video", "audio", "metadata", "tag")
    settings = "os",  "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    requires = (
        "libcurl/7.69.1",
        "libzen/0.4.38",
        "tinyxml2/8.0.0",
        "zlib/1.2.11",
    )

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("MediaInfoLib", self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_ZENLIB"] = False
        self._cmake.definitions["BUILD_ZLIB"] = False
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        os.rename("Findtinyxml2.cmake", "FindTinyXML.cmake")
        tools.replace_in_file("FindTinyXML.cmake", "tinyxml2_LIBRARIES", "TinyXML_LIBRARIES")

    def build(self):
        if not self.options["libzen"].enable_unicode:
            raise ConanInvalidConfiguration("This package requires libzen with unicode support")
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("License.html", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["mediainfo"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
        self.cpp_info.names["cmake_find_package"] = "MediaInfoLib"
        self.cpp_info.names["cmake_find_package_multi"] = "MediaInfoLib"
