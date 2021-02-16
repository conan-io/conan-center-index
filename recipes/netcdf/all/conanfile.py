from conans import CMake, ConanFile, tools
import glob
import os


class NetcdfConan(ConanFile):
    name = "netcdf"
    description = "The Unidata network Common Data Form (netCDF) is an interface for scientific data access and a freely-distributed software library that provides an implementation of the interface."
    topics = ("unidata", "unidata-netcdf", "networking")
    license = "BSD-3-Clause"
    homepage = "https://github.com/Unidata/netcdf-c"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "patches/**"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "netcdf4": [True, False],
        "with_hdf5": [True, False],
        "cdf5": [True, False],
        "dap": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "netcdf4": True,
        "with_hdf5": True,
        "cdf5": True,
        "dap": True,
    }
    generators = "cmake_find_package", "cmake_find_package_multi", "cmake"

    _cmake = None

    @property
    def _with_hdf5(self):
        return self.options.with_hdf5 or self.options.netcdf4

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
        if self._with_hdf5:
            self.requires("hdf5/1.12.0")
        if self.options.dap:
            self.requires("libcurl/7.73.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("netcdf-c-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_UTILITIES"] = False
        self._cmake.definitions["ENABLE_TESTS"] = False

        self._cmake.definitions["ENABLE_NETCDF_4"] = self.options.netcdf4
        self._cmake.definitions["ENABLE_CDF5"] = self.options.cdf5
        self._cmake.definitions["ENABLE_DAP"] = self.options.dap
        self._cmake.definitions["USE_HDF5"] = self.options.with_hdf5
        self._cmake.definitions["NC_FIND_SHARED_LIBS"] = self.options.with_hdf5 and self.options["hdf5"].shared
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYRIGHT", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        os.unlink(os.path.join(self.package_folder, "bin", "nc-config"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.settings")
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        for fn in glob.glob(os.path.join(self.package_folder, "bin", "*")):
            if "netcdf" not in os.path.basename(fn):
                os.unlink(fn)

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "netcdf"
        self.cpp_info.names["cmake_find_package"] = "netCDF"
        self.cpp_info.names["cmake_find_package_multi"] = "netCDF"
        self.cpp_info.components["libnetcdf"].libs = ["netcdf"]
        self.cpp_info.components["libnetcdf"].names["cmake_find_package"] = "netcdf"
        self.cpp_info.components["libnetcdf"].names["cmake_find_package_multi"] = "netcdf"
        if self._with_hdf5:
            self.cpp_info.components["libnetcdf"].requires.append("hdf5::hdf5")
        if self.options.dap:
            self.cpp_info.components["libnetcdf"].requires.append("libcurl::libcurl")
        if self.settings.os == "Linux":
            self.cpp_info.components["libnetcdf"].system_libs = ["dl", "m"]
        elif self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.components["libnetcdf"].defines.append("DLL_NETCDF")
