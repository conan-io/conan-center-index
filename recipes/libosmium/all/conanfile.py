import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class LibosmiumConan(ConanFile):
    name = "libosmium"
    description = "A fast and flexible C++ library for working with OpenStreetMap data"
    license = "BSL-1.0"
    homepage = "https://osmcode.org/libosmium/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("openstreetmap", "osm", "basemap", "gis", "geography", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "pbf": [True, False],
        "xml": [True, False],
        "geos": [True, False],
        "gdal": [True, False],
        "proj": [True, False],
        "lz4": [True, False],
    }
    default_options = {
        "pbf": True,
        "xml": True,
        "geos": True,
        "gdal": False,
        "proj": True,
        "lz4": True,
    }
    options_description = {
        # https://github.com/osmcode/libosmium/blob/v2.20.0/cmake/FindOsmium.cmake#L30-L37
        "pbf": "include libraries needed for PBF input and output",
        "xml": "include libraries needed for XML input and output",
        "geos": "include if you want to use any of the GEOS functions",
        "gdal": "include if you want to use any of the OGR functions",
        "proj": "include if you want to use any of the Proj.4 functions",
        "lz4": "include support for LZ4 compression of PBF files",
    }

    def export_sources(self):
        copy(self, "libosmium-official-vars.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.pbf:
            self.requires("protozero/1.7.1")
        if self.options.xml:
            self.requires("expat/[>=2.6.2 <3]")
            self.requires("bzip2/1.0.8")
        if self.options.pbf or self.options.xml:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.geos:
            self.requires("geos/3.12.0")
        if self.options.gdal:
            self.requires("gdalcpp/1.3.0")
        if self.options.proj:
            self.requires("proj/9.3.1")
        if self.options.lz4:
            self.requires("lz4/1.9.4")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _modules_rel_dir(self):
        return os.path.join("lib", "cmake", "libosmium")

    @property
    def _module_rel_path(self):
        return os.path.join(self._modules_rel_dir, "libosmium-official-vars.cmake")

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "include", "osmium"), os.path.join(self.package_folder, "include", "osmium"))
        copy(self, "libosmium-official-vars.cmake", self.source_folder, os.path.join(self.package_folder, self._modules_rel_dir))

    def package_info(self):
        # https://github.com/osmcode/libosmium/blob/master/cmake/FindOsmium.cmake
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Osmium")

        self.cpp_info.builddirs.append(os.path.join("lib", "cmake", "libosmium"))
        self.cpp_info.set_property("cmake_build_modules", [self._module_rel_path])

        def _add_component(name, reqs, threads=False):
            component = self.cpp_info.components[name]
            component.bindirs = []
            component.libdirs = []
            component.requires = reqs
            if threads and self.settings.os in ["Linux", "FreeBSD"]:
                component.system_libs.append("pthread")
            component.defines = ["_LARGEFILE_SOURCE", "_FILE_OFFSET_BITS=64"]
            if is_msvc(self):
                # https://github.com/osmcode/libosmium/blob/v2.20.0/cmake/FindOsmium.cmake#L316-L337
                component.cxxflags.extend(["-wd4996", "-wd4068", "-wd4715", "-wd4351", "-wd4503"])
                component.defines.extend(["NOMINMAX", "WIN32_LEAN_AND_MEAN", "_CRT_SECURE_NO_WARNINGS"])

        if self.options.pbf:
            _add_component("pbf", ["protozero::protozero", "zlib::zlib"], threads=True)
            if self.options.lz4:
                self.cpp_info.components["pbf"].requires.append("lz4")
        if self.options.xml:
            _add_component("xml", ["expat::expat", "bzip2::bzip2", "zlib::zlib"], threads=True)
        if self.options.pbf and self.options.xml:
            _add_component("io", ["pbf", "xml"])
        if self.options.geos:
            _add_component("geos", ["geos::geos"])
        if self.options.gdal:
            _add_component("gdal", ["gdalcpp::gdalcpp"])
        if self.options.proj:
            _add_component("proj", ["proj::proj"])
        if self.options.lz4:
            _add_component("lz4", ["lz4::lz4"])
            self.cpp_info.components["io"].defines.append("OSMIUM_WITH_LZ4")
