import os
from pathlib import Path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, export_conandata_patches, get, replace_in_file, rmdir, save, apply_conandata_patches, rename, rm
from conan.tools.scm import Version

required_conan_version = ">=2.0"


class OsrmConan(ConanFile):
    name = "osrm"
    description = "Open Source Routing Machine: high performance routing engine designed to run on OpenStreetMap data."
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://project-osrm.org/"
    topics = ("routing", "routing-engine", "map-matching", "traveling-salesman", "isochrones", "osm", "openstreetmap")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_tools": [True, False],
        "build_routed": [True, False],
        "enable_assertions": [True, False],
        "enable_lto": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_tools": False,
        "build_routed": False,
        "enable_assertions": False,
        "enable_lto": False,
    }
    options_description = {
        "build_tools": "Build OSRM tools",
        "build_routed": "Build osrm-routed HTTP server",
        "enable_assertions": "Use assertions in release mode",
        "enable_lto": "Use LTO if available",
    }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.build_type == "Debug":
            del self.options.enable_assertions

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["osmium"].pbf = True
        self.options["osmium"].xml = True
        self.options["osmium"].geos = False
        self.options["osmium"].gdal = False
        self.options["osmium"].proj = False
        self.options["osmium"].lz4 = False

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.86.0", transitive_headers=True, transitive_libs=True)
        self.requires("bzip2/1.0.8")
        self.requires("expat/[>=2.6.2 <3]")
        self.requires("libosmium/2.20.0")
        self.requires("lua/5.4.6")
        self.requires("onetbb/2021.12.0")
        self.requires("zlib/1.3.1")
        # unvendored deps
        self.requires("flatbuffers/1.12.0", transitive_headers=True, transitive_libs=True) # newer versions are not compatible
        self.requires("fmt/10.2.1")
        self.requires("mapbox-geometry/2.0.3")
        self.requires("mapbox-variant/1.2.0", transitive_headers=True)
        self.requires("microtar/0.1.0")
        self.requires("rapidjson/cci.20230929")
        self.requires("sol2/3.3.1")
        # TODO
        # self.requires("mapbox-cheap-ruler/0")
        # self.requires("vtzero/0")

    def validate(self):
        check_min_cppstd(self, 17)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if not self.dependencies["libosmium"].options.pbf or not self.dependencies["libosmium"].options.xml:
            raise ConanInvalidConfiguration("libosmium must be built with PBF and XML support")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.18 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

        # Disable subdirs
        save(self, os.path.join(self.source_folder, "unit_tests", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "src", "benchmarks", "CMakeLists.txt"), "")

        # Fix an irrelevant generator expression error during .pc file generation
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        '"$<TARGET_LINKER_FILE:${engine_lib}>"', '"${engine_lib}"')

        # Disable vendored deps
        for subdir in self.source_path.joinpath("third_party").iterdir():
            if subdir.name not in ["vtzero", "microtar"] and not subdir.name.startswith("cheap-ruler"):
                rmdir(self, subdir)
                save(self, subdir.joinpath("CMakeLists.txt"), "")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), " $<TARGET_OBJECTS:MICROTAR>", "")

        # Add missing includes.
        # TODO: submit upstream
        path = Path(self.source_folder, "include", "util", "coordinate.hpp")
        path.write_text("#include <cstdint>\n" + path.read_text())
        path = Path(self.source_folder, "src", "util", "opening_hours.cpp")
        path.write_text("#include <cstdint>\n" + path.read_text())
        path = Path(self.source_folder, "include", "util", "query_heap.hpp")
        path.write_text("#include <cstdint>\n" + path.read_text())
        path = Path(self.source_folder, "include", "extractor", "suffix_table.hpp")
        path.write_text("#include <vector>\n" + path.read_text())

        if Version(self.dependencies["boost"].ref.version) >= "1.85":
            # The header has been removed from Boost
            replace_in_file(self, os.path.join(self.source_folder, "include", "util", "lua_util.hpp"),
                            "#include <boost/filesystem/convenience.hpp>", "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_PROJECT_OSRM_INCLUDE"] = "conan_deps.cmake"
        tc.cache_variables["ENABLE_CONAN"] = False
        tc.cache_variables["BUILD_TOOLS"] = self.options.build_tools
        tc.cache_variables["BUILD_ROUTED"] = self.options.build_routed
        tc.cache_variables["ENABLE_ASSERTIONS"] = self.options.get_safe("enable_assertions", False)
        tc.cache_variables["ENABLE_LTO"] = self.options.enable_lto
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Doxygen"] = True
        if self.settings.compiler in ["gcc", "clang", "apple-clang"]:
            # TODO: should probably be fixed instead
            # include/sol/stack_field.hpp:116:61: error: array subscript ‘const char [30][0]’ is partly outside array bounds of ‘const char [18]’ [-Werror=array-bounds=]
            tc.extra_cxxflags.append("-Wno-array-bounds")
            # Disable -Werror=deprecated-declarations due to std::is_pod in C++20
            tc.extra_cxxflags.append("-Wno-deprecated-declarations")
            # include/updater/csv_file_parser.hpp:108:45: error: top-level comma expression in array subscript is deprecated [-Werror=comma-subscript]
            tc.extra_cxxflags.append("-Wno-comma-subscript")
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.TXT", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rename(self, os.path.join(self.package_folder, "share"),
               os.path.join(self.package_folder, "res"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LibOSRM")
        self.cpp_info.set_property("cmake_target_name", "LibOSRM::LibOSRM")
        self.cpp_info.set_property("pkg_config_name", "libosrm")

        self.cpp_info.includedirs.append(os.path.join("include", "osrm"))
        self.cpp_info.resdirs = ["res"]
        self.cpp_info.libs = [
            "osrm",
            "osrm_contract",
            "osrm_customize",
            "osrm_extract",
            "osrm_guidance",
            "osrm_partition",
            "osrm_store",
            "osrm_update",
        ]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "rt"])
