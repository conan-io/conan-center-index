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

    def requirements(self):
        self.requires.add("boost/1.72.0")
        self.requires.add("expat/2.2.9")
        self.requires.add("minizip/1.2.11")
        self.requires.add("uriparser/0.9.3")
        self.requires.add("zlib/1.2.11")

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
        # Libs ordered following linkage order:
        # - kmlconvenience is a dependency of kmlregionator
        # - kmlengine is a dependency of kmlregionator and kmlconvenience
        # - kmldom is a dependency of kmlregionator, kmlconvenience and kmlengine
        # - kmlbase is a dependency of kmlregionator, kmlconvenience, kmlengine, kmldom and kmlxsd
        self.cpp_info.libs = ["kmlregionator", "kmlconvenience", "kmlengine", "kmldom", "kmlxsd", "kmlbase"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("LIBKML_DLL")
