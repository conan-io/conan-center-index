import os
import glob
from conans import ConanFile, CMake, tools


class NetcdfConan(ConanFile):
    name = "netcdf"
    description = ("NetCDF is a set of software libraries and "
                   "self-describing, machine-independent data "
                   "formats that support the creation, access, "
                   "and sharing of array-oriented scientific data.")
    license = "BSD-3-Clause"
    homepage = "https://www.unidata.ucar.edu/software/netcdf/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("array", "dataset", "scientific")

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_netcdf4": [True, False],
        "with_dap": [True, False],
        "with_utilities": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_netcdf4": True,
        "with_dap": True,
        "with_utilities": True,
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
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_netcdf4:
            self.requires("hdf5/1.12.0")
        if self.options.with_dap:
            self.requires("libcurl/7.70.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "netcdf-c-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            cmake = CMake(self)
            cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.package_folder
            cmake.definitions["ENABLE_NETCDF_4"] = self.options.with_netcdf4
            cmake.definitions["ENABLE_DAP"] = self.options.with_dap
            cmake.definitions["BUILD_UTILITIES"] = self.options.with_utilities
            cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
            cmake.definitions["ENABLE_TESTS"] = False
            cmake.definitions["NC_FIND_SHARED_LIBS"] = self.options["hdf5"].shared

            cmake.configure(
                source_folder=self._source_subfolder,
                build_folder=self._build_subfolder
            )
            self._cmake = cmake

        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        for filename in glob.glob(
                os.path.join(self.package_folder, "lib", "*.la")):
            os.remove(filename)
        for filename in glob.glob(
                os.path.join(self.package_folder, "lib", "*.settings")):
            os.remove(filename)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "netCDF"
        self.cpp_info.names["cmake_find_package_multi"] = "netCDF"
        self.cpp_info.libs = ["netcdf"]
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
