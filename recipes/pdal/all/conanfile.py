import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building, can_run
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

    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_unwind": [True, False],
        "with_xml": [True, False],
        "with_lzma": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "with_unwind": False,
        "with_xml": True,
        "with_lzma": True,
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
        if self.settings.os not in ["Linux", "FreeBSD"]:
            self.options.rm_safe("with_unwind")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True, transitive_libs=True)
        self.requires("gdal/3.8.3", transitive_headers=True, transitive_libs=True)
        self.requires("h3/4.1.0")
        self.requires("json-schema-validator/2.3.0")
        self.requires("libcurl/[>=7.78.0 <9]") # for arbiter
        self.requires("libgeotiff/1.7.1")
        self.requires("nanoflann/1.5.2", transitive_headers=True, transitive_libs=True)
        self.requires("nlohmann_json/3.11.3", transitive_headers=True, transitive_libs=True)
        self.requires("openssl/[>=1.1 <4]") # for arbiter
        self.requires("proj/9.3.1", transitive_headers=True, transitive_libs=True)
        self.requires("rapidxml/1.13", transitive_headers=True) # for arbiter
        self.requires("utfcpp/4.0.4")
        self.requires("zlib/[>=1.2.11 <2]", transitive_headers=True, transitive_libs=True) # for arbiter
        if self.options.with_xml:
            self.requires("libxml2/2.12.5", transitive_headers=True, transitive_libs=True)
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")
        if self.options.with_lzma:
            self.requires("xz_utils/5.4.5")
        if self.options.get_safe("with_unwind"):
            self.requires("libunwind/1.8.0")
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
        # TODO: add postgresql support

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("pdal shared build doesn't support MT runtime with Visual Studio")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PDAL_HAVE_HDF5"] = False
        tc.variables["PDAL_HAVE_ZSTD"] = self.options.with_zstd
        tc.variables["PDAL_HAVE_ZLIB"] = True
        tc.variables["PDAL_HAVE_LZMA"] = self.options.with_lzma
        tc.variables["PDAL_HAVE_LIBXML2"] = self.options.with_xml
        # https://github.com/PDAL/PDAL/blob/2.7.0/cmake/options.cmake
        tc.variables["BUILD_PLUGIN_CPD"] = False
        tc.variables["BUILD_PLUGIN_DRACO"] = False
        tc.variables["BUILD_PLUGIN_E57"] = False
        tc.variables["BUILD_PLUGIN_FBX"] = False
        tc.variables["BUILD_PLUGIN_HDF"] = False
        tc.variables["BUILD_PLUGIN_ICEBRIDGE"] = False
        tc.variables["BUILD_PLUGIN_MATLAB"] = False
        tc.variables["BUILD_PLUGIN_MBIO"] = False
        tc.variables["BUILD_PLUGIN_NITF"] = False
        tc.variables["BUILD_PLUGIN_OPENSCENEGRAPH"] = False
        tc.variables["BUILD_PLUGIN_PGPOINTCLOUD"] = False
        tc.variables["BUILD_PLUGIN_RDBLIB"] = False
        tc.variables["BUILD_PLUGIN_RIVLIB"] = False
        tc.variables["BUILD_PLUGIN_TEASER"] = False
        tc.variables["BUILD_PLUGIN_TILEDB"] = False
        tc.variables["BUILD_PLUGIN_TRAJECTORY"] = False
        tc.variables["BUILD_TOOLS_NITFWRAP"] = False
        tc.variables["ENABLE_CTEST"] = False
        tc.variables["WITH_ABSEIL"] = False
        tc.variables["WITH_BACKTRACE"] = self.options.get_safe("with_unwind", False)
        tc.variables["WITH_COMPLETION"] = False
        tc.variables["WITH_TESTS"] = False
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_PostgreSQL"] = True
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_Libexecinfo"] = True
        if cross_building(self) and can_run(self):
            # Workaround for dimbuilder not being found when cross-compiling on macOS
            tc.variables["DIMBUILDER_EXECUTABLE"] = os.path.join(self.build_folder, "src", "bin", "dimbuilder")
        tc.generate()

        # For the namespace injection in _patch_sources() below
        self.dependencies["nlohmann_json"].cpp_info.includedirs.append(
            os.path.join(self.dependencies["nlohmann_json"].package_folder, "include", "nlohmann")
        )
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        top_cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")

        # Ensure only Conan-generated Find modules are used
        rm(self, "Find*.cmake", os.path.join(self.source_folder, "cmake", "modules"))

        for cmake_module in [
            # Remove .cmake modules for unvendored dependencies
            "h3",
            "nlohmann",
            "schema-validator",
            "utfcpp",
            # proj.cmake does not use find_package() and is not compatible
            "proj",
        ]:
            cmake_module = os.path.join(self.source_folder, "cmake", f"{cmake_module}.cmake")
            assert os.path.exists(cmake_module), f"{cmake_module} not found"
            save(self, cmake_module, "")

        # Unvendor nlohmann
        rmdir(self, os.path.join(self.source_folder, "vendor", "nlohmann"))
        save(self, os.path.join(self.source_folder, "vendor", "nlohmann", "nlohmann", "json.hpp"),
             "#include <json.hpp>\nnamespace NL = nlohmann;")
        # Overwrite JsonFwd.hpp since it's only compatible with nlohmann_json/3.10.15
        save(self, os.path.join(self.source_folder, "pdal", "JsonFwd.hpp"),
             "#include <nlohmann/json.hpp>\nnamespace NL = nlohmann;")
        # Unvendor h3
        rmdir(self, os.path.join(self.source_folder, "vendor", "h3"))
        save(self, os.path.join(self.source_folder, "vendor", "h3", "CMakeLists.txt"), "")
        replace_in_file(self, top_cmakelists, "H3_PREFIX=PDALH3", "")
        # Unvendor eigen
        rmdir(self, os.path.join(self.source_folder, "vendor", "eigen"))
        # Unvendor nanoflann
        rmdir(self, os.path.join(self.source_folder, "vendor", "nanoflann"))
        replace_in_file(self, os.path.join(self.source_folder, "pdal", "private", "KDImpl.hpp"),
                        "#include <nanoflann/nanoflann.hpp>", "#include <nanoflann.hpp>")
        # Unvendor utfcpp
        rmdir(self, os.path.join(self.source_folder, "vendor", "utfcpp"))
        save(self, os.path.join(self.source_folder, "vendor", "utfcpp", "CMakeLists.txt"), "")
        # Unvendor schema-validator
        rmdir(self, os.path.join(self.source_folder, "vendor", "schema-validator"))
        save(self, os.path.join(self.source_folder, "vendor", "schema-validator", "CMakeLists.txt"), "")
        save(self, os.path.join(self.source_folder, "vendor", "schema-validator", "json-schema.hpp"),
             "#include <nlohmann/json-schema.hpp>\n")
        replace_in_file(self, top_cmakelists, "${JSON_SCHEMA_LIB_NAME}", "")

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

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_target_file),
            {"pdalcpp": "PDAL::PDAL"},
        )

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
        self.cpp_info.set_property("cmake_target_aliases", ["pdalcpp"])
        self.cpp_info.set_property("pkg_config_name", "pdal")

        self.cpp_info.libs = ["pdalcpp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "9.0":
            self.cpp_info.system_libs.append("stdc++fs")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "PDAL"
        self.cpp_info.names["cmake_find_package_multi"] = "PDAL"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_target_file]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_target_file]
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
