from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class MatioConan(ConanFile):
    name = "matio"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/matio/"
    description = "Matio is a C library for reading and writing binary MATLAB MAT files."
    topics = ("conan", "matlab", "mat-file", "file-format", "hdf5")
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    exports_sources = "CMakeLists.txt", "patches/*"
    options = {
        "shared": [True, False],
        "extended_sparse": [True, False],
        "fPIC": [True, False],
        "mat73": [True, False],
        "with_hdf5": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "extended_sparse": True,
        "fPIC": True,
        "mat73": True,
        "with_hdf5": True,
        "with_zlib": True,
    }

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_hdf5:
            self.requires("hdf5/1.12.1")
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")

    def validate(self):
        if not self.options.with_hdf5 and self.options.mat73:
            raise ConanInvalidConfiguration("Support of version 7.3 MAT files requires HDF5")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["MATIO_EXTENDED_SPARSE"] = self.options.extended_sparse
        self._cmake.definitions["MATIO_PIC"] = self.options.get_safe("fPIC", True)
        self._cmake.definitions["MATIO_SHARED"] = self.options.shared
        self._cmake.definitions["MATIO_MAT73"] = self.options.mat73
        self._cmake.definitions["MATIO_WITH_HDF5"] = self.options.with_hdf5
        self._cmake.definitions["MATIO_WITH_ZLIB"] = self.options.with_zlib
        self._cmake.definitions["HDF5_USE_STATIC_LIBRARIES"] = self.options.with_hdf5 and not self.options["hdf5"].shared
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
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
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
