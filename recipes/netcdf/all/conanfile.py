from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file
import os

required_conan_version = ">=1.52.0"


class NetcdfConan(ConanFile):
    name = "netcdf"
    description = (
        "The Unidata network Common Data Form (netCDF) is an interface for "
        "scientific data access and a freely-distributed software library "
        "that provides an implementation of the interface."
    )
    topics = "unidata", "unidata-netcdf", "networking"
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

    @property
    def _with_hdf5(self):
        return self.options.with_hdf5 or self.options.netcdf4

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self._with_hdf5:
                self.requires("hdf5/1.13.1")
        if self.options.dap or self.options.byterange:
            self.requires("libcurl/7.85.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_UTILITIES"] = False
        tc.variables["ENABLE_TESTS"] = False
        tc.variables["ENABLE_FILTER_TESTING"] = False

        tc.variables["ENABLE_NETCDF_4"] = self.options.netcdf4
        tc.variables["ENABLE_CDF5"] = self.options.cdf5
        tc.variables["ENABLE_DAP"] = self.options.dap
        tc.variables["ENABLE_BYTERANGE"] = self.options.byterange
        tc.variables["USE_HDF5"] = self.options.with_hdf5
        tc.variables["NC_FIND_SHARED_LIBS"] = self.options.with_hdf5 and self.dependencies["hdf5"].options.shared

        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"

        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYRIGHT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rm(self, "nc-config", os.path.join(self.package_folder, "bin"))
        rm(self, "*.settings", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.os == "Windows" and self.options.shared:
            for vc_file in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
                rm(self, vc_file, os.path.join(self.package_folder, "bin"))
            rm(self, "*[!.dll]", os.path.join(self.package_folder, "bin"))
        else:
            rmdir(self, os.path.join(self.package_folder, "bin"))

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
