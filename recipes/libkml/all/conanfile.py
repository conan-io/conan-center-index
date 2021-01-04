import os

from conans import ConanFile, CMake, tools

class LibkmlConan(ConanFile):
    name = "libkml"
    description = "Reference implementation of OGC KML 2.2"
    license = "BSD-3-Clause"
    topics = ("conan", "libkml", "kml", "ogc", "geospatial")
    homepage = "https://github.com/libkml/libkml"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

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

    def requirements(self):
        self.requires("boost/1.73.0")
        self.requires("expat/2.2.9")
        self.requires("minizip/1.2.11")
        self.requires("uriparser/0.9.4")
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        # TODO:
        # - do not export LibKML:: namespace
        # - libkml depends on boost header only
        self.cpp_info.names["cmake_find_package"] = "LibKML"
        self.cpp_info.names["cmake_find_package_multi"] = "LibKML"
        # kmlbase
        self.cpp_info.components["kmlbase"].libs = ["kmlbase"]
        if self.settings.os == "Linux":
            self.cpp_info.components["kmlbase"].system_libs.append("m")
        self.cpp_info.components["kmlbase"].requires = [
            "boost::boost", "expat::expat", "minizip::minizip",
            "uriparser::uriparser", "zlib::zlib"
        ]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["kmlbase"].defines.append("LIBKML_DLL")
        # kmlxsd
        self.cpp_info.components["kmlxsd"].libs = ["kmlxsd"]
        self.cpp_info.components["kmlxsd"].requires = ["boost::boost", "kmlbase"]
        # kmldom
        self.cpp_info.components["kmldom"].libs = ["kmldom"]
        self.cpp_info.components["kmldom"].requires = ["boost::boost", "kmlbase"]
        # kmlengine
        self.cpp_info.components["kmlengine"].libs = ["kmlengine"]
        self.cpp_info.components["kmlengine"].requires = ["boost::boost", "kmldom", "kmlbase"]
        if self.settings.os == "Linux":
            self.cpp_info.components["kmlengine"].system_libs.append("m")
        # kmlconvenience
        self.cpp_info.components["kmlconvenience"].libs = ["kmlconvenience"]
        self.cpp_info.components["kmlconvenience"].requires = ["boost::boost", "kmlengine", "kmldom", "kmlbase"]
        # kmlregionator
        self.cpp_info.components["kmlregionator"].libs = ["kmlregionator"]
        self.cpp_info.components["kmlregionator"].requires = ["kmlconvenience", "kmlengine", "kmldom", "kmlbase"]
