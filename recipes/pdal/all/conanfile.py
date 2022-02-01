from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PdalConan(ConanFile):
    name = "pdal"
    description = "PDAL is Point Data Abstraction Library. GDAL for point cloud data."
    topics = ("pdal", "gdal", "point-cloud-data", "lidar")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pdal.io"
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_unwind": [True, False],
        "with_xml": [True, False],
        "with_lazperf": [True, False],
        "with_laszip": [True, False],
        "with_zlib": [True, False],
        "with_lzma": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_unwind": False,
        "with_xml": True,
        "with_lazperf": False, # TODO: should be True
        "with_laszip": True,
        "with_zlib": True,
        "with_lzma": False,
        "with_zstd": True,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_unwind

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        # TODO package improvements:
        # - switch from vendored arbiter (not in CCI). disabled openssl and curl are deps of arbiter
        # - switch from vendor/nlohmann to nlohmann_json (in CCI)
        self.requires("boost/1.77.0")
        self.requires("eigen/3.4.0")
        self.requires("gdal/3.3.3")
        self.requires("libcurl/7.79.1.0") # mandatory dependency of arbiter (to remove if arbiter is unvendored)
        self.requires("libgeotiff/1.7.0")
        self.requires("nanoflann/1.3.2")
        if self.options.with_xml:
            self.requires("libxml2/2.9.12")
        if self.options.with_zstd:
            self.requires("zstd/1.5.0")
        if self.options.with_lazperf:
            raise ConanInvalidConfiguration("lazperf recipe not yet available in CCI")
        if self.options.with_laszip:
            self.requires("laszip/3.4.3")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.get_safe("with_unwind"):
            self.requires("libunwind/1.5.0")

    @property
    def _required_boost_components(self):
        return ["filesystem"]

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < 5:
            raise ConanInvalidConfiguration ("This compiler version is unsupported")
        if self.options.shared and self.settings.compiler == "Visual Studio" and "MT" in str(self.settings.compiler.runtime):
            raise ConanInvalidConfiguration("pdal shared doesn't support MT runtime with Visual Studio")
        miss_boost_required_comp = any(getattr(self.options["boost"], "without_{}".format(boost_comp), True) for boost_comp in self._required_boost_components)
        if self.options["boost"].header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration("{0} requires non header-only boost with these components: {1}".format(self.name, ", ".join(self._required_boost_components)))
        if hasattr(self, "settings_build") and tools.cross_building(self):
            raise ConanInvalidConfiguration("pdal doesn't support cross-build yet")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PDAL_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["WITH_TESTS"] = False
        self._cmake.definitions["WITH_LAZPERF"] = self.options.with_lazperf
        self._cmake.definitions["WITH_LASZIP"] = self.options.with_laszip
        self._cmake.definitions["WITH_STATIC_LASZIP"] = True # doesn't really matter but avoids to inject useless definition
        self._cmake.definitions["WITH_ZSTD"] = self.options.with_zstd
        self._cmake.definitions["WITH_ZLIB"] = self.options.with_zlib
        self._cmake.definitions["WITH_LZMA"] = self.options.with_lzma
        # disable plugin that requires postgresql
        self._cmake.definitions["BUILD_PLUGIN_PGPOINTCLOUD"] = False
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # drop conflicting CMake files
        # LASzip works fine
        for module in ("ZSTD", "ICONV", "GeoTIFF", "Curl"):
            os.remove(os.path.join(self._source_subfolder, "cmake", "modules", "Find"+module+".cmake"))

        top_cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        util_cmakelists = os.path.join(self._source_subfolder, "pdal", "util", "CMakeLists.txt")

        # disabling libxml2 support is only done via patching
        if not self.options.with_xml:
            tools.replace_in_file(top_cmakelists, "include(${PDAL_CMAKE_DIR}/libxml2.cmake)", "")
        # disabling libunwind support is only done via patching
        if not self.options.get_safe("with_unwind", False):
            tools.replace_in_file(util_cmakelists, "include(${PDAL_CMAKE_DIR}/unwind.cmake)", "")
        # remove vendored eigen
        tools.rmdir(os.path.join(self._source_subfolder, "vendor", "eigen"))
        # remove vendored nanoflann. include path is patched
        tools.rmdir(os.path.join(self._source_subfolder, "vendor", "nanoflann"))
        # remove vendored boost
        tools.rmdir(os.path.join(self._source_subfolder, "vendor", "pdalboost"))
        tools.replace_in_file(top_cmakelists, "add_subdirectory(vendor/pdalboost)", "")
        tools.replace_in_file(util_cmakelists, "${PDAL_BOOST_LIB_NAME}", "${CONAN_LIBS}")
        tools.replace_in_file(os.path.join(self._source_subfolder, "pdal", "util", "FileUtils.cpp"),
                              "pdalboost::", "boost::")
        # No rpath manipulation
        tools.replace_in_file(top_cmakelists, "include(${PDAL_CMAKE_DIR}/rpath.cmake)", "")
        # No reexport
        tools.replace_in_file(top_cmakelists,
                              "set(PDAL_REEXPORT \"-Wl,-reexport_library,$<TARGET_FILE:${PDAL_UTIL_LIB_NAME}>\")",
                              "")
        # fix static build
        if not self.options.shared:
            tools.replace_in_file(top_cmakelists, "add_definitions(\"-DPDAL_DLL_EXPORT=1\")", "")
            tools.replace_in_file(top_cmakelists,
                                  "${PDAL_BASE_LIB_NAME} ${PDAL_UTIL_LIB_NAME}",
                                  "${PDAL_BASE_LIB_NAME} ${PDAL_UTIL_LIB_NAME} ${PDAL_ARBITER_LIB_NAME} ${PDAL_KAZHDAN_LIB_NAME}")
            tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "macros.cmake"),
                                  "        install(TARGETS ${_name}",
                                  "    endif()\n    if (PDAL_LIB_TYPE STREQUAL \"STATIC\" OR NOT ${_library_type} STREQUAL \"STATIC\")\n         install(TARGETS ${_name}")
            tools.replace_in_file(util_cmakelists,
                                  "PDAL_ADD_FREE_LIBRARY(${PDAL_UTIL_LIB_NAME} SHARED ${PDAL_UTIL_SOURCES})",
                                  "PDAL_ADD_FREE_LIBRARY(${PDAL_UTIL_LIB_NAME} ${PDAL_LIB_TYPE} ${PDAL_UTIL_SOURCES})")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "pdal-config*")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "PDAL"
        self.cpp_info.names["cmake_find_package_multi"] = "PDAL"
        self.cpp_info.names["pkg_config"] = "pdal"
        pdal_base_name = "pdalcpp" if self.settings.os == "Windows" or tools.is_apple_os(self.settings.os) else "pdal_base"
        self.cpp_info.libs = [pdal_base_name, "pdal_util"]
        if not self.options.shared:
            self.cpp_info.libs.extend(["pdal_arbiter", "pdal_kazhdan"])
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.extend(["dl", "m"])
            elif self.settings.os == "Windows":
                # dependency of pdal_arbiter
                self.cpp_info.system_libs.append("shlwapi")
        self.cpp_info.requires = [
            "boost::filesystem", "eigen::eigen", "gdal::gdal",
            "libcurl::libcurl", "libgeotiff::libgeotiff", "nanoflann::nanoflann"
        ]
        if self.options.with_xml:
            self.cpp_info.requires.append("libxml2::libxml2")
        if self.options.with_zstd:
            self.cpp_info.requires.append("zstd::zstd")
        if self.options.with_laszip:
            self.cpp_info.requires.append("laszip::laszip")
        if self.options.with_zlib:
            self.cpp_info.requires.append("zlib::zlib")
        if self.options.with_lzma:
            self.cpp_info.requires.append("xz_utils::xz_utils")
        if self.options.get_safe("with_unwind"):
            self.cpp_info.requires.append("libunwind::libunwind")
