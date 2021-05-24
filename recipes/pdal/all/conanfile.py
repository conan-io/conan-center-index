from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PdalConan(ConanFile):
    name = "pdal"
    description = "PDAL is Point Data Abstraction Library. GDAL for point cloud data."
    topics = ("conan", "pdal", "gdal", "point-cloud-data", "lidar")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pdal.io"
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_unwind": [True, False],
        "with_xml": [True, False],
        "with_laszip": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_unwind": False,
        "with_xml": True,
        "with_laszip": True,
        "with_zlib": True,
        "with_zstd": True,
    }

    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_unwind

    def configure(self):
        # upstream export/install targets do not work with static builds
        if not self.options.shared:
            raise ConanInvalidConfiguration("pdal does not support building as a static lib yet")
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < 5:
            raise ConanInvalidConfiguration ("This compiler version is unsupported")

    def requirements(self):
        # TODO package improvements:
        # - switch from vendored arbiter (not in CCI). disabled openssl and curl are deps of arbiter
        # - switch from vendor/nlohmann to nlohmann_json (in CCI)
        self.requires("boost/1.76.0")
        self.requires("eigen/3.3.9")
        self.requires("gdal/3.2.1")
        self.requires("libcurl/7.75.0") # mandotory dependency of arbiter (to remove if arbiter is unvendored)
        self.requires("libgeotiff/1.6.0")
        self.requires("nanoflann/1.3.2")
        if self.options.with_xml:
            self.requires("libxml2/2.9.10")
        if self.options.with_zstd:
            self.requires("zstd/1.5.0")
        if self.options.with_laszip:
            self.requires("laszip/3.4.3")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.get_safe("with_unwind"):
            self.requires("libunwind/1.5.0")

    @property
    def _required_boost_components(self):
        return ["filesystem"]

    def validate(self):
        miss_boost_required_comp = any(getattr(self.options["boost"], "without_{}".format(boost_comp), True) for boost_comp in self._required_boost_components)
        if self.options["boost"].header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration("{0} requires non header-only boost with these components: {1}".format(self.name, ", ".join(self._required_boost_components)))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["WITH_TESTS"] = False
        self._cmake.definitions["WITH_LAZPERF"] = False
        self._cmake.definitions["WITH_LASZIP"] = self.options.with_laszip
        self._cmake.definitions["WITH_ZSTD"] = self.options.with_zstd
        self._cmake.definitions["WITH_ZLIB"] = self.options.with_zlib
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
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "m"])
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
        if self.options.get_safe("with_unwind"):
            self.cpp_info.requires.append("libunwind::libunwind")
