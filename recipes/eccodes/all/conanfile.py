import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file

required_conan_version = ">=1.53.0"


class EccodesConan(ConanFile):
    name = "eccodes"
    description = "ECMWF ecCodes is a package developed by ECMWF which provides an API and a set of tools for decoding and encoding GRIB, BUFR and GTS formats."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ecmwf/eccodes"
    topics = ("grib", "bufr", "gts", "ecmwf", "meteorology")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_jasper": [True, False],
        "with_openjpeg": [True, False],
        "with_netcdf": [True, False],
        "fortran": [True, False],
        "with_threads": [True, False],
        "build_tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": False,
        "with_jasper": True,
        "with_openjpeg": True,
        "with_netcdf": True,
        "fortran": False,
        "with_threads": True,
        "build_tools": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.fortran:
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libaec/1.1.4")
        self.requires("eckit/2.1.0")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_jasper:
            self.requires("jasper/4.2.4")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.2")
        if self.options.with_netcdf:
            self.requires("netcdf/4.8.1")

    def build_requirements(self):
        self.tool_requires("ecbuild/3.14.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_AEC"] = True
        tc.variables["ENABLE_ECKIT_GEO"] = True
        tc.variables["ENABLE_JPG"] = self.options.with_jasper or self.options.with_openjpeg
        tc.variables["ENABLE_JPG_LIBJASPER"] = self.options.with_jasper
        tc.variables["ENABLE_JPG_LIBOPENJPEG"] = self.options.with_openjpeg
        tc.variables["ENABLE_PNG"] = self.options.with_png
        tc.variables["ENABLE_NETCDF"] = self.options.with_netcdf
        tc.variables["ENABLE_FORTRAN"] = self.options.fortran
        tc.variables["ENABLE_MEMFS"] = False
        tc.variables["ENABLE_PYTHON"] = False
        tc.variables["ENABLE_BUILD_TOOLS"] = self.options.build_tools
        tc.variables["ENABLE_EXAMPLES"] = False
        tc.variables["ENABLE_TESTS"] = False
        tc.variables["ENABLE_EXTRA_TESTS"] = False
        tc.variables["ENABLE_ECCODES_THREADS"] = self.options.with_threads
        tc.variables["ENABLE_PKGCONFIG"] = False
        tc.variables["INSTALL_ECCODES_DEFINITIONS"] = True
        tc.variables["INSTALL_ECCODES_SAMPLES"] = True
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        # We need to define eckit_geo target if it doesn't exist so ecbuild finds it
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        
        replacement = (
            "if( eccodes_HAVE_ECKIT_GEO AND NOT TARGET eckit_geo )\n"
            "    ecbuild_find_package(NAME eckit REQUIRED)\n"
            "    if( NOT TARGET eckit_geo )\n"
            "        if( TARGET eckit::eckit )\n"
            "            add_library(eckit_geo INTERFACE IMPORTED)\n"
            "            target_link_libraries(eckit_geo INTERFACE eckit::eckit eckit::eckit)\n"
            "        elseif( TARGET eckit )\n"
            "            add_library(eckit_geo INTERFACE IMPORTED)\n"
            "            target_link_libraries(eckit_geo INTERFACE eckit eckit)\n"
            "        else()\n"
            "            ecbuild_critical(\"eckit has not been built with ECKIT_GEO enabled\")\n"
            "        endif()\n"
            "    endif()\n"
            "endif()"
        )
        
        with open(cmakelists, "r", encoding="utf-8") as f:
            content = f.read()
        
        target_str = (
            "if( eccodes_HAVE_ECKIT_GEO AND NOT TARGET eckit_geo )\n"
            "    ecbuild_find_package(NAME eckit VERSION 1.27 REQUIRED)\n"
            "    if( NOT TARGET eckit_geo )\n"
            "        ecbuild_critical(\"eckit has not been built with ECKIT_GEO enabled\")\n"
            "    endif()\n"
            "endif()"
        )
        
        if target_str in content:
            content = content.replace(target_str, replacement)
        else:
            self.output.warn("Could not find expected eckit_geo check in CMakeLists.txt to patch")
            
        if self.options.with_netcdf:
            netcdf_patch = (
                "find_package( netCDF REQUIRED )\n"
                "set( NetCDF_C_EXTRA_LIBRARIES netCDF::netcdf )\n"
                "ecbuild_add_option( FEATURE NETCDF"
            )
            content = content.replace("ecbuild_add_option( FEATURE NETCDF", netcdf_patch)

        content = content.replace("add_subdirectory( tests )", "if(ENABLE_TESTS)\nadd_subdirectory( tests )\nendif()")
        content = content.replace("add_subdirectory( examples )", "if(ENABLE_EXAMPLES)\nadd_subdirectory( examples )\nendif()")

        with open(cmakelists, "w", encoding="utf-8") as f:
            f.write(content)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # Clean up unwanted cmake files and pkgconfig
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "eccodes")
        self.cpp_info.set_property("cmake_target_name", "eccodes::eccodes")
        
        # Libraries built by eccodes
        self.cpp_info.libs = ["eccodes"]
        if self.options.fortran:
            self.cpp_info.libs.append("eccodes_f90")
            
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
