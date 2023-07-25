import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir, save, load
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
        "with_lazperf": False,  # TODO: should be True
        "with_laszip": True,
        "with_zlib": True,
        "with_lzma": False,
        "with_zstd": True,
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
        self.requires("boost/1.82.0")
        self.requires("eigen/3.4.0", transitive_headers=True)
        self.requires("gdal/3.4.3", transitive_headers=True)
        self.requires("libcurl/8.1.2", force=True)  # mandatory dependency of arbiter (to remove if arbiter is unvendored)
        self.requires("openssl/[>=1.1 <4]")
        self.requires("libgeotiff/1.7.1")
        self.requires("nanoflann/1.4.3")
        if self.options.with_xml:
            self.requires("libxml2/2.11.4", transitive_headers=True)
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")
        if self.options.with_laszip:
            self.requires("laszip/3.4.3", transitive_headers=True)
        if self.options.with_zlib:
            self.requires("zlib/1.2.13", transitive_headers=True)
        if self.options.with_lzma:
            self.requires("xz_utils/5.4.2")
        if self.options.get_safe("with_unwind"):
            self.requires("libunwind/1.6.2")
        # TODO package improvements:
        # - switch from vendored arbiter (not in CCI)
        # - unvendor nlohmann_json
        # - add draco
        # - add openscenegraph

        # Handle conflicts between gdal and other deps
        self.requires("libtiff/4.5.0", override=True)
        self.requires("libdeflate/1.18", override=True)
        self.requires("sqlite3/3.42.0", override=True)

    @property
    def _required_boost_components(self):
        return ["filesystem"]

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < 5:
            raise ConanInvalidConfiguration("This compiler version is unsupported")
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
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("pdal doesn't support cross-build yet")
        if self.options.with_lazperf:
            raise ConanInvalidConfiguration("lazperf recipe not yet available in CCI")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PDAL_BUILD_STATIC"] = not self.options.shared
        tc.variables["WITH_TESTS"] = False
        tc.variables["WITH_LAZPERF"] = self.options.with_lazperf
        tc.variables["WITH_LASZIP"] = self.options.with_laszip
        # doesn't really matter but avoids to inject useless definition
        tc.variables["WITH_STATIC_LASZIP"] = True
        tc.variables["WITH_ZSTD"] = self.options.with_zstd
        tc.variables["WITH_ZLIB"] = self.options.with_zlib
        tc.variables["WITH_LZMA"] = self.options.with_lzma
        # disable plugin that requires postgresql
        tc.variables["BUILD_PLUGIN_PGPOINTCLOUD"] = False
        # Workarounds for different library names
        tc.variables["geotiff_FOUND"] = True
        tc.variables["gdal_FOUND"] = True
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        top_cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        util_cmakelists = os.path.join(self.source_folder, "pdal", "util", "CMakeLists.txt")
        # Provide these dependencies via the CMakeLists.txt in the recipe instead
        for cmake_module in [
            "gdal",
            "geotiff",
            # "lazperf",
            "laszip",
            "zlib",
            "lzma",
            "zstd",
            "libxml2",
            # "dimension",
            # "arbiter",
            # "nlohmann",
            "openssl",
        ]:
            replace_in_file(self, top_cmakelists, f"include(${{PDAL_CMAKE_DIR}}/{cmake_module}.cmake)", "")

        # disabling libxml2 support is only done via patching
        if not self.options.with_xml:
            replace_in_file(self, top_cmakelists, "include(${PDAL_CMAKE_DIR}/libxml2.cmake)", "")
        # disabling libunwind support is only done via patching
        if not self.options.get_safe("with_unwind", False):
            replace_in_file(self, util_cmakelists, "include(${PDAL_CMAKE_DIR}/unwind.cmake)", "")
        for vendored_lib in ["eigen", "nanoflann", "pdalboost"]:
            rmdir(self, os.path.join(self.source_folder, "vendor", vendored_lib))
        replace_in_file(self, top_cmakelists, "add_subdirectory(vendor/pdalboost)", "")
        replace_in_file(self, util_cmakelists, "${PDAL_BOOST_LIB_NAME}", "Boost::filesystem")
        replace_in_file(self, os.path.join(self.source_folder, "pdal", "util", "FileUtils.cpp"),
                        "pdalboost::", "boost::")
        # No rpath manipulation
        replace_in_file(self, top_cmakelists, "include(${PDAL_CMAKE_DIR}/rpath.cmake)", "")
        # No reexport
        replace_in_file(self, top_cmakelists,
                        'set(PDAL_REEXPORT "-Wl,-reexport_library,$<TARGET_FILE:${PDAL_UTIL_LIB_NAME}>")', "")
        # fix static build
        if not self.options.shared:
            replace_in_file(self, top_cmakelists, 'add_definitions("-DPDAL_DLL_EXPORT=1")', "")
            replace_in_file(self, top_cmakelists,
                            "${PDAL_BASE_LIB_NAME} ${PDAL_UTIL_LIB_NAME}",
                            ("${PDAL_BASE_LIB_NAME} ${PDAL_UTIL_LIB_NAME} "
                             "${PDAL_ARBITER_LIB_NAME} ${PDAL_KAZHDAN_LIB_NAME}"))
            replace_in_file(self, os.path.join(self.source_folder, "cmake", "macros.cmake"),
                "install(TARGETS ${_name}",
                ("endif()\n"
                 'if (PDAL_LIB_TYPE STREQUAL "STATIC" OR NOT ${_library_type} STREQUAL "STATIC")\n'
                 "    install(TARGETS ${_name}"))
            replace_in_file(self, util_cmakelists,
                            "PDAL_ADD_FREE_LIBRARY(${PDAL_UTIL_LIB_NAME} SHARED ${PDAL_UTIL_SOURCES})",
                            "PDAL_ADD_FREE_LIBRARY(${PDAL_UTIL_LIB_NAME} ${PDAL_LIB_TYPE} ${PDAL_UTIL_SOURCES})")

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
            {f"{self._pdal_base_name}": f"PDAL::{self._pdal_base_name}", "pdal_util": "PDAL::pdal_util"},
        )

    def _create_cmake_module_variables(self, module_file):
        pdal_version = Version(self.version)
        content = textwrap.dedent(f"""\
            set(PDAL_LIBRARIES {self._pdal_base_name} pdal_util)
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

    @property
    def _pdal_base_name(self):
        return "pdalcpp" if self.settings.os == "Windows" or is_apple_os(self) else "pdal_base"

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PDAL")
        self.cpp_info.set_property("cmake_target_name", "PDAL::PDAL")
        self.cpp_info.set_property("cmake_build_modules", [self._module_vars_file])
        self.cpp_info.set_property("pkg_config_name", "pdal")

        # pdal_base
        self.cpp_info.components["pdal_base"].set_property("cmake_target_name", self._pdal_base_name)
        self.cpp_info.components["pdal_base"].libs = [self._pdal_base_name]
        if not self.options.shared:
            self.cpp_info.components["pdal_base"].libs.extend(["pdal_arbiter", "pdal_kazhdan"])
            if self.settings.os == "Windows":
                # dependency of pdal_arbiter
                self.cpp_info.components["pdal_base"].system_libs.append("shlwapi")
        self.cpp_info.components["pdal_base"].requires = [
            "pdal_util",
            "eigen::eigen",
            "gdal::gdal",
            "libcurl::libcurl",
            "libgeotiff::libgeotiff",
            "nanoflann::nanoflann",
            "openssl::openssl",
        ]
        if self.options.with_xml:
            self.cpp_info.components["pdal_base"].requires.append("libxml2::libxml2")
        if self.options.with_zstd:
            self.cpp_info.components["pdal_base"].requires.append("zstd::zstd")
        if self.options.with_laszip:
            self.cpp_info.components["pdal_base"].requires.append("laszip::laszip")
        if self.options.with_zlib:
            self.cpp_info.components["pdal_base"].requires.append("zlib::zlib")
        if self.options.with_lzma:
            self.cpp_info.components["pdal_base"].requires.append("xz_utils::xz_utils")

        # pdal_util
        self.cpp_info.components["pdal_util"].set_property("cmake_target_name", "pdal_util")
        self.cpp_info.components["pdal_util"].libs = ["pdal_util"]
        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["pdal_util"].system_libs.extend(["dl", "m"])
        self.cpp_info.components["pdal_util"].requires = ["boost::filesystem"]
        if self.options.get_safe("with_unwind"):
            self.cpp_info.components["pdal_util"].requires.append("libunwind::libunwind")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "PDAL"
        self.cpp_info.names["cmake_find_package_multi"] = "PDAL"
        self.cpp_info.components["pdal_base"].names["cmake_find_package"] = self._pdal_base_name
        self.cpp_info.components["pdal_base"].names["cmake_find_package_multi"] = self._pdal_base_name
        self.cpp_info.components["pdal_base"].build_modules["cmake_find_package"] = [
            self._module_target_file, self._module_vars_file,
        ]
        self.cpp_info.components["pdal_base"].build_modules["cmake_find_package_multi"] = [
            self._module_target_file, self._module_vars_file,
        ]
