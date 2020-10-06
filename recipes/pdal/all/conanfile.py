import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration

class PdalConan(ConanFile):
    name = "pdal"
    description = "PDAL is Point Data Abstraction Library. GDAL for point cloud data."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pdal.io"
    license = "BSD"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_xml": [True, False],
               "with_zstd": [True, False],
               "with_laszip": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_xml": True,
                       "with_zstd": True,
                       "with_laszip": True}
    topics = ("conan", "pdal", "gdal")

    _source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires("gdal/3.1.4")
        self.requires("libgeotiff/1.6.0")
        if self.options.with_xml:
            self.requires("libxml2/2.9.10")
        if self.options.with_zstd:
            self.requires("zstd/1.4.5")
        if self.options.with_laszip:
            self.requires("laszip/3.4.3")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        # upstream export/install targets do not work with static builds
        if not self.options.shared:
            raise ConanInvalidConfiguration("pdal does not support building as a static lib yet")
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("PDAL-%s-src" % self.version, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        cmake.definitions["WITH_TESTS"] = False
        cmake.definitions["WITH_LAZPERF"] = False
        cmake.definitions["WITH_LASZIP"] = self.options.with_laszip
        cmake.definitions["WITH_ZSTD"] = self.options.with_zstd
        cmake.definitions["WITH_ZLIB"] = True
        # disable plugin that requires postgresql
        cmake.definitions["BUILD_PLUGIN_PGPOINTCLOUD"] = False
        # disabling libxml2 support is only done via patching
        if not self.options.with_xml:
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "CMakeLists.txt"),
                "include(${PDAL_CMAKE_DIR}/libxml2.cmake)",
                "#include(${PDAL_CMAKE_DIR}/libxml2.cmake)")
        cmake.configure()
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # drop conflicting CMake files
        # LASzip works fine
        for module in ('ZSTD', 'ICONV', 'GeoTIFF', 'Curl'):
            os.remove(os.path.join(self._source_subfolder, "cmake", "modules", "Find"+module+".cmake"))

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "PDAL"
        self.cpp_info.names["cmake_find_package_multi"] = "PDAL"
        self.cpp_info.names["pkg_config"] = "PDAL"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "m"])
