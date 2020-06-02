import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class Hdf4Conan(ConanFile):
    name = "hdf4"
    description = "HDF4 is a data model, library, and file format for storing and managing data."
    license = "BSD-3-Clause"
    topics = ("conan", "hdf4", "hdf", "data")
    homepage = "https://portal.hdfgroup.org/display/HDF4/HDF4"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "jpegturbo": [True, False],
        "szip_support": [None, "with_libaec", "with_szip"],
        "szip_encoding": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "jpegturbo": False,
        "szip_support": None,
        "szip_encoding": False
    }

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if not bool(self.options.szip_support):
            del self.options.szip_encoding
        elif self.options.szip_support == "with_szip" and \
             self.options.szip_encoding and \
             not self.options["szip"].enable_encoding:
            raise ConanInvalidConfiguration("encoding must be enabled in the dependency (szip:enable_encoding=True)")

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.jpegturbo:
            self.requires("libjpeg-turbo/2.0.4")
        else:
            self.requires("libjpeg/9d")
        if self.options.szip_support == "with_libaec":
            self.requires("libaec/1.0.4")
        elif self.options.szip_support == "with_szip":
            self.requires("szip/2.1.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("hdf-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["HDF4_EXTERNALLY_CONFIGURED"] = True
        self._cmake.definitions["HDF4_EXTERNAL_LIB_PREFIX"] = ""
        self._cmake.definitions["HDF4_NO_PACKAGES"] = True
        self._cmake.definitions["ONLY_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["HDF4_ENABLE_COVERAGE"] = False
        self._cmake.definitions["HDF4_ENABLE_DEPRECATED_SYMBOLS"] = True
        self._cmake.definitions["HDF4_ENABLE_JPEG_LIB_SUPPORT"] = True # HDF can't compile without libjpeg or libjpeg-turbo
        self._cmake.definitions["HDF4_ENABLE_Z_LIB_SUPPORT"] = True # HDF can't compile without zlib
        self._cmake.definitions["HDF4_ENABLE_SZIP_SUPPORT"] = bool(self.options.szip_support)
        self._cmake.definitions["HDF4_ENABLE_SZIP_ENCODING"] = self.options.get_safe("szip_encoding") or False
        self._cmake.definitions["HDF4_PACKAGE_EXTLIBS"] = False
        self._cmake.definitions["HDF4_BUILD_XDR_LIB"] = True
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["HDF4_INSTALL_INCLUDE_DIR"] = os.path.join(self.package_folder, "include", "hdf4")
        self._cmake.definitions["HDF4_BUILD_FORTRAN"] = False
        self._cmake.definitions["HDF4_BUILD_UTILS"] = False
        self._cmake.definitions["HDF4_BUILD_TOOLS"] = False
        self._cmake.definitions["HDF4_BUILD_EXAMPLES"] = False
        self._cmake.definitions["HDF4_BUILD_JAVA"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.remove(os.path.join(self.package_folder, "lib", "libhdf4.settings"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "hdf"
        self.cpp_info.libs = self._get_ordered_libs()
        self.cpp_info.includedirs.append(os.path.join(self.package_folder, "include", "hdf4"))
        if self.options.shared:
            self.cpp_info.defines.append("H4_BUILT_AS_DYNAMIC_LIB")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]

    def _get_ordered_libs(self):
        libs = ["mfhdf", "xdr", "hdf"]
        # See config/cmake_ext_mod/HDFMacros.cmake
        if self.settings.os == "Windows" and self.settings.compiler != "gcc" and not self.options.shared:
            libs = ["lib" + lib for lib in libs]
        if self.settings.build_type == "Debug":
            debug_postfix = "_D" if self.settings.os == "Windows" else "_debug"
            libs = [lib + debug_postfix for lib in libs]
        return libs
