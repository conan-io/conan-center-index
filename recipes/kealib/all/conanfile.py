from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.32.0"


class KealibConan(ConanFile):
    name = "kealib"
    description = "C++ library providing complete access to the KEA image format."
    license = "MIT"
    topics = ("conan", "kealib", "image", "raster")
    homepage = "https://github.com/ubarsc/kealib"
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
        self.options["hdf5"].enable_cxx = True
        self.options["hdf5"].hl = True

    def requirements(self):
        self.requires("hdf5/1.12.0")

    def validate(self):
        if not (self.options["hdf5"].enable_cxx and self.options["hdf5"].hl):
            raise ConanInvalidConfiguration("kealib requires hdf5 with cxx and hl enabled.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("{0}-{0}-{1}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["HDF5_USE_STATIC_LIBRARIES"] = not self.options["hdf5"].shared
        self._cmake.definitions["HDF5_PREFER_PARALLEL"] = False # TODO: rely on self.options["hdf5"].parallel when implemented in hdf5 recipe
        self._cmake.definitions["LIBKEA_WITH_GDAL"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self, self)
