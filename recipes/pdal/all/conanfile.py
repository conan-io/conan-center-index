import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rm, rmdir, save, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class PdalConan(ConanFile):
    name = "pdal"
    description = "PDAL is Point Data Abstraction Library. GDAL for point cloud data."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pdal.io"
    topics = ("gdal", "point-cloud-data", "lidar")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_unwind": [True, False],
        "with_xml": [True, False],
        "with_zlib": [True, False],
        "with_lzma": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_unwind": False,
        "with_xml": True,
        "with_zlib": True,
        "with_lzma": False,
        "with_zstd": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12.0",
        }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            self.options.rm_safe("with_unwind")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("arbiter/cci.20231005", transitive_headers=True, transitive_libs=True)
        self.requires("boost/1.83.0")
        self.requires("eigen/3.4.0", transitive_headers=True, transitive_libs=True)
        self.requires("gdal/3.8.0", transitive_headers=True, transitive_libs=True)
        self.requires("json-schema-validator/2.2.0")
        self.requires("libgeotiff/1.7.1")
        self.requires("nanoflann/1.5.0", transitive_headers=True, transitive_libs=True)
        self.requires("nlohmann_json/3.11.2", transitive_headers=True, transitive_libs=True)
        self.requires("proj/9.3.0", transitive_headers=True, transitive_libs=True)
        self.requires("utfcpp/4.0.1")
        if self.options.with_xml:
            self.requires("libxml2/2.11.5", transitive_headers=True, transitive_libs=True)
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]", transitive_headers=True, transitive_libs=True)
        if self.options.with_lzma:
            self.requires("xz_utils/5.4.4")
        if self.options.get_safe("with_unwind"):
            self.requires("libunwind/1.7.2")
        # TODO: unvendor kazhdan (not on CCI, https://github.com/mkazhdan/PoissonRecon)
        # TODO: unvendor lazperf (not on CCI, https://github.com/hobuinc/laz-perf)
        # TODO: unvendor lepcc (not on CCI, https://github.com/Esri/lepcc)
        # TODO: add arrow support (requires parquet)
        # TODO: add cpd support (not on CCI, https://github.com/gadomski/cpd)
        # TODO: add ceres support
        # TODO: add draco support
        # TODO: add hdf5 support
        # TODO: add iconv support
        # TODO: add libe57format support (and unvendor)
        # TODO: add libexecinfo support
        # TODO: add libpq support
        # TODO: add mbsystem support (not on CCI, https://github.com/dwcaress/MB-System)
        # TODO: add nitro support (not on CCI, https://github.com/hobu/nitro)
        # TODO: add openscenegraph support
        # TODO: add teaserpp support (not on CCI, https://github.com/MIT-SPARK/TEASER-plusplus)
        # TODO: add tiledb support

    @property
    def _required_boost_components(self):
        return ["filesystem"]

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("pdal shared doesn't support MT runtime with Visual Studio")

        miss_boost_required_comp = any(
            self.dependencies["boost"].options.get_safe(f"without_{boost_comp}", True)
            for boost_comp in self._required_boost_components
        )
        if self.dependencies["boost"].options.header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration(
                f"{self.name} requires non header-only boost with these components: "
                + ", ".join(self._required_boost_components)
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PDAL_BUILD_STATIC"] = not self.options.shared
        tc.variables["WITH_TESTS"] = False
        tc.variables["PDAL_HAVE_ZSTD"] = self.options.with_zstd
        tc.variables["PDAL_HAVE_ZLIB"] = self.options.with_zlib
        tc.variables["PDAL_HAVE_LZMA"] = self.options.with_lzma
        # disable plugin that requires postgresql
        tc.variables["BUILD_PLUGIN_PGPOINTCLOUD"] = False
        tc.generate()

        # For the namespace injection in _patch_sources() below
        self.dependencies["nlohmann_json"].cpp_info.includedirs.append(
            os.path.join(self.dependencies["nlohmann_json"].package_folder, "include", "nlohmann")
        )
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        top_cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        util_cmakelists = os.path.join(self.source_folder, "pdal", "util", "CMakeLists.txt")

        # Provide these dependencies via the CMakeLists.txt in the recipe instead
        for cmake_module in [
            "arbiter",
            "gdal",
            "geotiff",
            "libxml2",
            "lzma",
            "nlohmann",
            "openssl",
            "proj,"
            "schema-validator",
            "utfcpp",
            "zlib",
            "zstd",
        ]:
            save(self, os.path.join(self.source_folder, "cmake", f"{cmake_module}.cmake"), "")
        # Unvendor arbiter
        rmdir(self, os.path.join(self.source_folder, "vendor", "arbiter"))
        save(self, os.path.join(self.source_folder, "vendor", "arbiter", "CMakeLists.txt"), "")
        # Unvendor nlohmann
        rmdir(self, os.path.join(self.source_folder, "vendor", "nlohmann"))
        save(self, os.path.join(self.source_folder, "vendor", "nlohmann", "nlohmann", "json.hpp"),
             "#include <json.hpp>\nnamespace NL = nlohmann;")
        # Overwrite JsonFwd.hpp since it's only compatible with nlohmann_json/3.10.15
        save(self, os.path.join(self.source_folder, "pdal", "JsonFwd.hpp"),
             "#include <nlohmann/json.hpp>\nnamespace NL = nlohmann;")
        # Unvendor eigen
        rmdir(self, os.path.join(self.source_folder, "vendor", "eigen"))
        # Unvendor nanoflann
        rmdir(self, os.path.join(self.source_folder, "vendor", "nanoflann"))
        replace_in_file(self, os.path.join(self.source_folder, "pdal", "private", "KDImpl.hpp"),
                        "#include <nanoflann/nanoflann.hpp>", "#include <nanoflann.hpp>")
        # Unvendor utfcpp
        rmdir(self, os.path.join(self.source_folder, "vendor", "utfcpp"))
        save(self, os.path.join(self.source_folder, "vendor", "utfcpp", "CMakeLists.txt"), "")
        #unvendor schema-validator
        rmdir(self, os.path.join(self.source_folder, "vendor", "schema-validator"))
        save(self, os.path.join(self.source_folder, "vendor", "schema-validator", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "vendor", "schema-validator", "json-schema.hpp"),
             "#include <nlohmann/json-schema.hpp>\n")
        replace_in_file(self, top_cmakelists, "${JSON_SCHEMA_LIB_NAME}", "")

        # Disabling libxml2 support is only possible via patching
        if not self.options.with_xml:
            replace_in_file(self, top_cmakelists, "include(${PDAL_CMAKE_DIR}/libxml2.cmake)", "")
        # Disabling libunwind support is only possible via patching
        if not self.options.get_safe("with_unwind", False):
            replace_in_file(self, util_cmakelists, "include(${PDAL_CMAKE_DIR}/unwind.cmake)", "")
        # Disable rpath manipulation
        replace_in_file(self, top_cmakelists, "include(${PDAL_CMAKE_DIR}/rpath.cmake)", "")
        # Disable copying of symbols from libpdal_util.dylib to libpdalcpp.dylib
        replace_in_file(self, top_cmakelists, "${PDAL_REEXPORT}", "")

        # TODO: should be turned into a patch and submitted upstream
        for header in [os.path.join(self.source_folder, "io", "private", "connector", "Connector.hpp"),
                       os.path.join(self.source_folder, "io", "private", "stac", "Utils.hpp")]:
            replace_in_file(self, header,
                            "#include <arbiter/arbiter.hpp>",
                            "#include <arbiter/arbiter.hpp>\n#include <nlohmann/json.hpp>")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"),
             ignore_case=True,
             keep_path=False)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "pdal-config*", os.path.join(self.package_folder, "bin"), recursive=True)
        self._create_cmake_module_variables(os.path.join(self.package_folder, self._module_vars_file))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_target_file),
            {"pdalcpp": "PDAL::pdalcpp", "pdal_util": "PDAL::pdal_util"},
        )

    def _create_cmake_module_variables(self, module_file):
        pdal_version = Version(self.version)
        content = textwrap.dedent(f"""\
            set(PDAL_LIBRARIES pdalcpp pdal_util)
            set(PDAL_VERSION_MAJOR {pdal_version.major})
            set(PDAL_VERSION_MINOR {pdal_version.minor})
            set(PDAL_VERSION_PATCH {pdal_version.patch})
        """)
        save(self, module_file, content)

    @property
    def _module_vars_file(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_target_file(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PDAL")
        self.cpp_info.set_property("cmake_target_name", "PDAL::PDAL")
        self.cpp_info.set_property("cmake_build_modules", [self._module_vars_file])
        self.cpp_info.set_property("pkg_config_name", "pdal")

        # pdal_base
        self.cpp_info.components["pdal_base"].set_property("cmake_target_name", "pdalcpp")
        self.cpp_info.components["pdal_base"].libs = ["pdalcpp"]
        if not self.options.shared:
            self.cpp_info.components["pdal_base"].libs.extend(["pdal_kazhdan", "pdal_lepcc"])
        self.cpp_info.components["pdal_base"].builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.components["pdal_base"].requires = [
            "pdal_util",
            "arbiter::arbiter",
            "eigen::eigen",
            "gdal::gdal",
            "json-schema-validator::json-schema-validator",
            "libgeotiff::libgeotiff",
            "nanoflann::nanoflann",
            "nlohmann_json::nlohmann_json",
            "proj::proj",
            "utfcpp::utfcpp",
        ]
        if self.options.with_xml:
            self.cpp_info.components["pdal_base"].requires.append("libxml2::libxml2")
        if self.options.with_zstd:
            self.cpp_info.components["pdal_base"].requires.append("zstd::zstd")
        if self.options.with_zlib:
            self.cpp_info.components["pdal_base"].requires.append("zlib::zlib")
        if self.options.with_lzma:
            self.cpp_info.components["pdal_base"].requires.append("xz_utils::xz_utils")

        # pdal_util
        self.cpp_info.components["pdal_util"].set_property("cmake_target_name", "pdal_util")
        if not self.options.shared:
            self.cpp_info.components["pdal_util"].libs = ["pdal_util"]
        self.cpp_info.components["pdal_util"].builddirs.append(os.path.join("lib", "cmake"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["pdal_util"].system_libs.extend(["dl", "m", "pthread"])
        self.cpp_info.components["pdal_util"].requires = [
            "boost::filesystem",
            "nlohmann_json::nlohmann_json",
            "utfcpp::utfcpp",
        ]
        if self.options.get_safe("with_unwind"):
            self.cpp_info.components["pdal_util"].requires.append("libunwind::libunwind")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "PDAL"
        self.cpp_info.names["cmake_find_package_multi"] = "PDAL"
        self.cpp_info.components["pdal_base"].names["cmake_find_package"] = "pdalcpp"
        self.cpp_info.components["pdal_base"].names["cmake_find_package_multi"] = "pdalcpp"
        self.cpp_info.components["pdal_base"].build_modules["cmake_find_package"] = [
            self._module_target_file, self._module_vars_file,
        ]
        self.cpp_info.components["pdal_base"].build_modules["cmake_find_package_multi"] = [
            self._module_target_file, self._module_vars_file,
        ]
