import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rm, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=2.1"


class PdalConan(ConanFile):
    name = "pdal"
    description = "PDAL is Point Data Abstraction Library. GDAL for point cloud data."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pdal.io"
    topics = ("gdal", "point-cloud-data", "lidar")

    # PDAL hardcodes set(PDAL_LIB_TYPE "SHARED") in cmake/libraries.cmake
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_xml": [True, False],
        "with_zlib": [True, False],
        "with_lzma": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "with_xml": True,
        "with_zlib": True,
        "with_lzma": False,
        "with_zstd": True,
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("gdal/3.8.3")
        self.requires("libcurl/[>=7.78]")
        self.requires("libgeotiff/[>=1.7]")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("proj/[>=9.0]")
        if self.options.with_xml:
            self.requires("libxml2/[>=2.12]")
        if self.options.with_zstd:
            self.requires("zstd/[>=1.5]")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11]")
        if self.options.with_lzma:
            self.requires("xz_utils/[>=5.4]")

    def validate(self):
        check_min_cppstd(self, 17)
        if is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support MT runtime (PDAL is always shared)."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["WITH_TESTS"] = False
        tc.cache_variables["WITH_ZSTD"] = self.options.with_zstd
        tc.cache_variables["WITH_ZLIB"] = self.options.with_zlib
        tc.cache_variables["WITH_LZMA"] = self.options.with_lzma
        tc.cache_variables["WITH_BACKTRACE"] = False
        tc.cache_variables["WITH_GCS"] = False
        tc.cache_variables["BUILD_PLUGIN_PGPOINTCLOUD"] = False
        tc.cache_variables["BUILD_PLUGIN_ICEBRIDGE"] = False
        tc.cache_variables["BUILD_PLUGIN_HDF"] = False
        tc.cache_variables["BUILD_PLUGIN_ARROW"] = False
        tc.cache_variables["BUILD_PLUGIN_DRACO"] = False
        tc.cache_variables["BUILD_PLUGIN_E57"] = False
        tc.cache_variables["BUILD_PLUGIN_FBXSDK"] = False
        tc.cache_variables["BUILD_PLUGIN_NITF"] = False
        tc.cache_variables["BUILD_PLUGIN_TILEDB"] = False
        tc.cache_variables["BUILD_PLUGIN_TRAJECTORY"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("libgeotiff", "cmake_file_name", "GeoTIFF")
        deps.set_property("libgeotiff", "cmake_additional_variables_prefixes", ["GEOTIFF"])
        deps.set_property("openssl", "cmake_additional_variables_prefixes", ["OPENSSL"])
        deps.set_property("proj", "cmake_file_name", "PROJ")
        deps.set_property("libcurl", "cmake_additional_variables_prefixes", ["CURL"])
        if self.options.with_zstd:
            deps.set_property("zstd", "cmake_file_name", "zstd")
            deps.set_property("zstd", "cmake_additional_variables_prefixes", ["ZSTD"])
        if self.options.with_zlib:
            deps.set_property("zlib", "cmake_additional_variables_prefixes", ["ZLIB"])
        if self.options.with_lzma:
            deps.set_property("xz_utils", "cmake_file_name", "LibLZMA")
            deps.set_property("xz_utils", "cmake_additional_variables_prefixes", ["LIBLZMA"])
        if self.options.with_xml:
            deps.set_property("libxml2", "cmake_file_name", "LibXml2")
            deps.set_property("libxml2", "cmake_additional_variables_prefixes", ["LIBXML2"])
        deps.generate()

    def _patch_sources(self):
        top_cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")

        # Inject find_package(OpenSSL) before arbiter so OPENSSL_FOUND is set
        replace_in_file(self, top_cmakelists,
                        "include(${PDAL_CMAKE_DIR}/arbiter.cmake)",
                        "find_package(OpenSSL REQUIRED)\n"
                        "include(${PDAL_CMAKE_DIR}/arbiter.cmake)")

        # Disable rpath manipulation (handled by Conan)
        replace_in_file(self, top_cmakelists,
                        "include(${PDAL_CMAKE_DIR}/rpath.cmake)", "")

        # Disable libxml2 if not wanted
        if not self.options.with_xml:
            replace_in_file(self, top_cmakelists,
                            "include(${PDAL_CMAKE_DIR}/libxml2.cmake)", "")

        # zstd.cmake uses find_package(zstd CONFIG) - needs PDAL_HAVE_ZSTD set
        # The original cmake module works with cmake_additional_variables_prefixes
        # setting ZSTD_FOUND, but we still need PDAL_HAVE_ZSTD
        zstd_cmake = os.path.join(self.source_folder, "cmake", "zstd.cmake")
        save(self, zstd_cmake, textwrap.dedent("""\
            option(WITH_ZSTD "Build support for Zstd." TRUE)
            if (WITH_ZSTD)
                find_package(zstd CONFIG QUIET)
                if (ZSTD_FOUND)
                    set(PDAL_HAVE_ZSTD 1)
                else()
                    set(WITH_ZSTD FALSE)
                endif()
            endif()
        """))

        # zlib.cmake - original uses ZLIB_FOUND which CMakeDeps provides
        zlib_cmake = os.path.join(self.source_folder, "cmake", "zlib.cmake")
        save(self, zlib_cmake, textwrap.dedent("""\
            option(WITH_ZLIB "Build support for zlib/deflate." TRUE)
            if (WITH_ZLIB)
                find_package(ZLIB REQUIRED)
                if (ZLIB_FOUND)
                    set(PDAL_HAVE_ZLIB 1)
                endif()
            endif()
        """))

        # lzma.cmake - bridge to LIBLZMA_* variables
        lzma_cmake = os.path.join(self.source_folder, "cmake", "lzma.cmake")
        save(self, lzma_cmake, textwrap.dedent("""\
            option(WITH_LZMA "Build support for LZMA" FALSE)
            if (WITH_LZMA)
                find_package(LibLZMA REQUIRED)
                if (LIBLZMA_FOUND)
                    set(PDAL_HAVE_LZMA 1)
                endif()
            endif()
        """))

        # libxml2.cmake - simplified with cmake_additional_variables_prefixes
        libxml2_cmake = os.path.join(self.source_folder, "cmake", "libxml2.cmake")
        save(self, libxml2_cmake, textwrap.dedent("""\
            get_property(EXISTS GLOBAL PROPERTY _LIBXML2_INCLUDED)
            if(EXISTS)
                return()
            endif()
            find_package(LibXml2)
            if (LIBXML2_FOUND)
                set(PDAL_HAVE_LIBXML2 1)
            endif()
            set_property(GLOBAL PROPERTY _LIBXML2_INCLUDED TRUE)
        """))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "pdal-config*", os.path.join(self.package_folder, "bin"))

        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_vars_file)
        )

    def _create_cmake_module_variables(self, module_file):
        pdal_version = Version(self.version)
        content = textwrap.dedent(f"""\
            set(PDAL_VERSION_MAJOR {pdal_version.major})
            set(PDAL_VERSION_MINOR {pdal_version.minor})
            set(PDAL_VERSION_PATCH {pdal_version.patch})
        """)
        save(self, module_file, content)

    @property
    def _module_vars_file(self):
        return os.path.join("lib", "cmake", "conan-official-pdal-variables.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PDAL")
        self.cpp_info.set_property("cmake_build_modules", [self._module_vars_file])
        self.cpp_info.set_property("pkg_config_name", "pdal")

        self.cpp_info.libs = ["pdalcpp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["shlwapi", "ws2_32"])

        self.cpp_info.requires = [
            "gdal::gdal",
            "libcurl::libcurl",
            "libgeotiff::libgeotiff",
            "openssl::openssl",
            "proj::proj",
        ]
        if self.options.with_xml:
            self.cpp_info.requires.append("libxml2::libxml2")
        if self.options.with_zstd:
            self.cpp_info.requires.append("zstd::zstd")
        if self.options.with_zlib:
            self.cpp_info.requires.append("zlib::zlib")
        if self.options.with_lzma:
            self.cpp_info.requires.append("xz_utils::xz_utils")

