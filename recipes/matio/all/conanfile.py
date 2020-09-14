from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class MatioConan(ConanFile):
    name = "matio"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/matio/"
    description = "Matio is a C library for reading and writing binary MATLAB MAT files."
    topics = ("conan", "matlab", "mat-file", "file-format", "hdf5")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/*"
    options = {
        "shared": [True, False],
        "extended_sparse": [True, False],
        "fPIC": [True, False],
        "mat73": [True, False],
        "with_hdf5": [None, "shared", "static"],
        "with_zlib": [None, "shared", "static"]
    }
    default_options = {
        "shared": False,
        "extended_sparse": True,
        "fPIC": True,
        "mat73": True,
        "with_hdf5": "static",
        "with_zlib": "static"
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def requirements(self):
        if self.options.get_safe("with_hdf5") not in (None, "None"):
            self.requires("hdf5/[>=1.8 <1.13]")
        if self.options.get_safe("with_zlib") not in (None, "None"):
            self.requires("zlib/[>=1.2.3]")

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def config_options(self):
        if self.settings.os == "Windows" or self.options.get_safe("shared"):
            del self.options.fPIC

    def configure(self):
        if self.options.get_safe("with_hdf5") not in (None, "None"):
            self.options["hdf5"].shared = self.options.with_hdf5 == "shared"
        if self.options.get_safe("with_zlib") not in (None, "None"):
            self.options["zlib"].shared = self.options.with_zlib == "shared"
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._patch_sources()
        self._cmake = CMake(self)
        self._cmake.definitions["MATIO_EXTENDED_SPARSE"] = self.options.extended_sparse
        if self.options.get_safe("fPIC"):
            self._cmake.definitions["MATIO_PIC"] = self.options.fPIC
        self._cmake.definitions["MATIO_SHARED"] = self.options.shared
        self._cmake.definitions["MATIO_MAT73"] = self.options.mat73
        self._cmake.definitions["MATIO_WITH_HDF5"] = self.options.get_safe("with_hdf5") not in (None, "None")
        self._cmake.definitions["MATIO_WITH_ZLIB"] = self.options.get_safe("with_zlib") not in (None, "None")
        if self.options.with_hdf5 not in (None, "None"):
            self._cmake.definitions["HDF5_USE_STATIC_LIBRARIES"] = self.options.with_hdf5 == "static"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        if self.options.with_hdf5 in (None, "None") and self.options.mat73:
            raise ConanInvalidConfiguration("Support of version 7.3 MAT files requires HDF5")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs = ["libmatio"]
        else:
            self.cpp_info.libs = ["matio"]
