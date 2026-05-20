import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    replace_in_file,
    rm,
    rmdir,
    save,
)
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=2.0.5"


class PdalConan(ConanFile):
    name = "pdal"
    description = "PDAL is Point Data Abstraction Library. GDAL for point cloud data."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pdal.io"
    topics = ("gdal", "point-cloud-data", "lidar")

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

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Eigen and nanoflann are vendored (private to shared lib, not in public headers)
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

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(f"{self.ref} does not support MT runtime with MSVC.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_TESTS"] = False
        tc.variables["WITH_ZSTD"] = self.options.with_zstd
        tc.variables["WITH_ZLIB"] = self.options.with_zlib
        tc.variables["WITH_LZMA"] = self.options.with_lzma
        tc.variables["WITH_BACKTRACE"] = False
        tc.variables["WITH_GCS"] = False
        tc.variables["BUILD_PLUGIN_PGPOINTCLOUD"] = False
        tc.variables["BUILD_PLUGIN_ICEBRIDGE"] = False
        tc.variables["BUILD_PLUGIN_HDF"] = False
        tc.variables["BUILD_PLUGIN_ARROW"] = False
        tc.variables["BUILD_PLUGIN_DRACO"] = False
        tc.variables["BUILD_PLUGIN_E57"] = False
        tc.variables["BUILD_PLUGIN_FBXSDK"] = False
        tc.variables["BUILD_PLUGIN_NITF"] = False
        tc.variables["BUILD_PLUGIN_TILEDB"] = False
        tc.variables["BUILD_PLUGIN_TRAJECTORY"] = False
        tc.generate()
        deps = CMakeDeps(self)
        # Override cmake_file_name to match what PDAL's find_package calls expect
        deps.set_property("libgeotiff", "cmake_file_name", "GeoTIFF")
        deps.set_property("proj", "cmake_file_name", "PROJ")
        if self.options.with_zstd:
            deps.set_property("zstd", "cmake_file_name", "ZSTD")
        if self.options.with_xml:
            deps.set_property("libxml2", "cmake_file_name", "LibXml2")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        top_cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")

        # Fix cmake/geotiff.cmake - bridge GeoTIFF_* vars to GEOTIFF_* vars
        geotiff_cmake = os.path.join(self.source_folder, "cmake", "geotiff.cmake")
        save(self, geotiff_cmake, textwrap.dedent("""\
            find_package(GeoTIFF REQUIRED)
            set(GEOTIFF_FOUND TRUE)
            set(GEOTIFF_INCLUDE_DIR "${GeoTIFF_INCLUDE_DIRS}")
            set(GEOTIFF_LIBRARY "${GeoTIFF_LIBRARIES}")
            set(PDAL_HAVE_LIBGEOTIFF 1)
        """))

        # Fix cmake/gdal.cmake - bridge plural to singular
        gdal_cmake = os.path.join(self.source_folder, "cmake", "gdal.cmake")
        save(self, gdal_cmake, textwrap.dedent("""\
            find_package(GDAL REQUIRED)
            set(GDAL_INCLUDE_DIR "${GDAL_INCLUDE_DIRS}")
            set(GDAL_LIBRARY "${GDAL_LIBRARIES}")
        """))

        # Fix cmake/curl.cmake - find curl and OpenSSL for arbiter
        curl_cmake = os.path.join(self.source_folder, "cmake", "curl.cmake")
        save(self, curl_cmake, textwrap.dedent("""\
            find_package(CURL REQUIRED)
            if (CURL_FOUND)
                set(CMAKE_THREAD_PREFER_PTHREAD TRUE)
                find_package(Threads REQUIRED)
                include_directories(${CURL_INCLUDE_DIR} ${CURL_INCLUDE_DIRS})
                if (WIN32)
                    add_definitions("-DWINDOWS")
                else()
                    add_definitions("-DUNIX")
                endif()
            endif()
            # OpenSSL is needed by arbiter; use target-based approach
            find_package(OpenSSL REQUIRED)
            set(OPENSSL_FOUND TRUE)
        """))

        # Patch arbiter CMakeLists.txt to use OpenSSL targets instead of
        # legacy variables (OPENSSL_INCLUDE_DIR/OPENSSL_LIBRARIES).
        # CMakeDeps only propagates include paths via target properties.
        arbiter_cmake = os.path.join(self.source_folder, "vendor", "arbiter", "CMakeLists.txt")
        replace_in_file(self, arbiter_cmake,
            "target_include_directories(${PDAL_ARBITER_LIB_NAME}\n"
            "        PRIVATE\n"
            "            ${OPENSSL_INCLUDE_DIR})\n"
            "    target_link_libraries(${PDAL_ARBITER_LIB_NAME}\n"
            "        PRIVATE\n"
            "            ${OPENSSL_LIBRARIES})",
            "target_link_libraries(${PDAL_ARBITER_LIB_NAME}\n"
            "        PRIVATE\n"
            "            OpenSSL::SSL OpenSSL::Crypto)"
        )

        # Fix cmake/proj.cmake - bridge PROJ_INCLUDE_DIRS to PROJ_INCLUDE_DIR
        proj_cmake = os.path.join(self.source_folder, "cmake", "proj.cmake")
        save(self, proj_cmake, textwrap.dedent("""\
            find_package(PROJ REQUIRED CONFIG)
            set(PROJ_INCLUDE_DIR "${PROJ_INCLUDE_DIRS}")
        """))

        # Fix cmake/zstd.cmake - use CMakeDeps-generated ZSTD variables
        zstd_cmake = os.path.join(self.source_folder, "cmake", "zstd.cmake")
        save(self, zstd_cmake, textwrap.dedent("""\
            option(WITH_ZSTD "Build support for Zstd." TRUE)
            if (WITH_ZSTD)
                find_package(ZSTD QUIET)
                if (ZSTD_FOUND)
                    set(ZSTD_INCLUDE_DIRS "${ZSTD_INCLUDE_DIRS}")
                    set(ZSTD_LIBRARIES "${ZSTD_LIBRARIES}")
                    set(PDAL_HAVE_ZSTD 1)
                else()
                    set(WITH_ZSTD FALSE)
                endif()
            endif()
        """))

        # Fix cmake/zlib.cmake - bridge plural to singular
        zlib_cmake = os.path.join(self.source_folder, "cmake", "zlib.cmake")
        save(self, zlib_cmake, textwrap.dedent("""\
            option(WITH_ZLIB "Build support for zlib/deflate." TRUE)
            if (WITH_ZLIB)
                find_package(ZLIB REQUIRED)
                if (ZLIB_FOUND)
                    set(ZLIB_INCLUDE_DIR "${ZLIB_INCLUDE_DIRS}")
                    set(ZLIB_LIBRARY "${ZLIB_LIBRARIES}")
                    set(PDAL_HAVE_ZLIB 1)
                endif()
            endif()
        """))

        # Fix cmake/lzma.cmake - bridge LibLZMA_* → LIBLZMA_*
        lzma_cmake = os.path.join(self.source_folder, "cmake", "lzma.cmake")
        save(self, lzma_cmake, textwrap.dedent("""\
            option(WITH_LZMA "Build support for LZMA" FALSE)
            if (WITH_LZMA)
                find_package(LibLZMA REQUIRED)
                set(LIBLZMA_FOUND ${LibLZMA_FOUND})
                set(LIBLZMA_INCLUDE_DIRS "${LibLZMA_INCLUDE_DIRS}")
                set(LIBLZMA_LIBRARIES "${LibLZMA_LIBRARIES}")
                if (LIBLZMA_FOUND)
                    set(PDAL_HAVE_LZMA 1)
                endif()
            endif()
        """))

        # Fix cmake/libxml2.cmake - bridge libxml2/LibXml2 to LIBXML2_*
        libxml2_cmake = os.path.join(self.source_folder, "cmake", "libxml2.cmake")
        save(self, libxml2_cmake, textwrap.dedent("""\
            get_property(EXISTS GLOBAL PROPERTY _LIBXML2_INCLUDED)
            if(EXISTS)
                return()
            endif()
            find_package(LibXml2)
            if (LibXml2_FOUND OR LIBXML2_FOUND)
                set(LIBXML2_FOUND TRUE)
                if (NOT LIBXML2_INCLUDE_DIR)
                    set(LIBXML2_INCLUDE_DIR "${LibXml2_INCLUDE_DIRS}")
                endif()
                if (NOT LIBXML2_LIBRARIES)
                    set(LIBXML2_LIBRARIES "${LibXml2_LIBRARIES}")
                endif()
                set(PDAL_HAVE_LIBXML2 1)
            endif()
            set_property(GLOBAL PROPERTY _LIBXML2_INCLUDED TRUE)
        """))

        # Override gcs.cmake - GCS disabled, OpenSSL bridge handled in curl.cmake
        gcs_cmake = os.path.join(self.source_folder, "cmake", "gcs.cmake")
        save(self, gcs_cmake, textwrap.dedent("""\
            option(WITH_GCS
                "Build with OpenSSL and others for Google storage IO support" FALSE)
        """))

        # Disable libxml2 support via patching if not wanted
        if not self.options.with_xml:
            replace_in_file(self, top_cmakelists,
                            "include(${PDAL_CMAKE_DIR}/libxml2.cmake)", "")

        # No rpath manipulation
        replace_in_file(self, top_cmakelists,
                        "include(${PDAL_CMAKE_DIR}/rpath.cmake)", "")

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
            set(PDAL_LIBRARIES pdalcpp)
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

