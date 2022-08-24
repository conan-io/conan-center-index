from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


class NetcdfConan(ConanFile):
    name = "netcdf"
    description = (
        "The Unidata network Common Data Form (netCDF) is an interface for "
        "scientific data access and a freely-distributed software library "
        "that provides an implementation of the interface."
    )
    topics = ("unidata", "unidata-netcdf", "networking")
    license = "BSD-3-Clause"
    homepage = "https://github.com/Unidata/netcdf-c"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "netcdf4": [True, False],
        "with_hdf5": [True, False],
        "cdf5": [True, False],
        "dap": [True, False],
        "byterange": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "netcdf4": True,
        "with_hdf5": True,
        "cdf5": True,
        "dap": True,
        "byterange": False,
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

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

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
            if self.version == "4.7.4":
                # 4.7.4 was built and tested with hdf5/1.12.0
                # It would be nice to upgrade to 1.12.1,
                # but when the byterange feature is enabled,
                # it triggers a compile error that was later patched in 4.8.x
                # So we will require the older hdf5 to keep the older behaviour.
                self.requires("hdf5/1.12.0")
            else:
                self.requires("hdf5/1.12.1")

        if self.options.dap or self.options.byterange:
            self.requires("libcurl/7.83.1")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["BUILD_UTILITIES"] = False
        self._cmake.definitions["ENABLE_TESTS"] = False
        self._cmake.definitions["ENABLE_FILTER_TESTING"] = False

        self._cmake.definitions["ENABLE_NETCDF_4"] = self.options.netcdf4
        self._cmake.definitions["ENABLE_CDF5"] = self.options.cdf5
        self._cmake.definitions["ENABLE_DAP"] = self.options.dap
        self._cmake.definitions["ENABLE_BYTERANGE"] = self.options.byterange
        self._cmake.definitions["USE_HDF5"] = self.options.with_hdf5
        self._cmake.definitions["NC_FIND_SHARED_LIBS"] = self.options.with_hdf5 and self.options["hdf5"].shared
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYRIGHT", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        os.unlink(os.path.join(self.package_folder, "bin", "nc-config"))
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.settings")
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.os == "Windows" and self.options.shared:
            for vc_file in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
                tools.files.rm(self, os.path.join(self.package_folder, "bin"), vc_file)
            tools.files.rm(self, os.path.join(self.package_folder, "bin"), "*[!.dll]")
        else:
            tools.files.rmdir(self, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "netCDF")
        self.cpp_info.set_property("cmake_target_name", "netCDF::netcdf")
        self.cpp_info.set_property("pkg_config_name", "netcdf")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libnetcdf"].libs = ["netcdf"]
        self.cpp_info.components["libnetcdf"].libdirs       = ["lib"]
        self.cpp_info.components["libnetcdf"].includedirs   = ["include"]
        if self._with_hdf5:
            self.cpp_info.components["libnetcdf"].requires.append("hdf5::hdf5")
        if self.options.dap or self.options.byterange:
            self.cpp_info.components["libnetcdf"].requires.append("libcurl::libcurl")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libnetcdf"].system_libs = ["dl", "m"]
        elif self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.components["libnetcdf"].defines.append("DLL_NETCDF")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "netCDF"
        self.cpp_info.names["cmake_find_package_multi"] = "netCDF"
        self.cpp_info.components["libnetcdf"].names["cmake_find_package"] = "netcdf"
        self.cpp_info.components["libnetcdf"].names["cmake_find_package_multi"] = "netcdf"
        self.cpp_info.components["libnetcdf"].set_property("cmake_target_name", "netCDF::netcdf")
        self.cpp_info.components["libnetcdf"].set_property("pkg_config_name", "netcdf")
