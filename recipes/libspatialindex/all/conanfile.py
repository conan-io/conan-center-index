from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get
from conan.tools.microsoft import is_msvc
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.50.0"


class LibspatialindexConan(ConanFile):
    name = "libspatialindex"
    description = "C++ implementation of R*-tree, an MVR-tree and a TPR-tree with C API."
    license = "MIT"
    topics = ("libspatialindex", "spatial-indexing", "tree")
    homepage = "https://github.com/libspatialindex/libspatialindex"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SIDX_BUILD_TESTS"] = False
        tc.variables["SIDX_BIN_SUBDIR"] = "bin"
        tc.variables["SIDX_LIB_SUBDIR"] = "lib"
        tc.variables["SIDX_INCLUDE_SUBDIR"] = "include"
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libspatialindex")
        self.cpp_info.set_property("pkg_config_name", "libspatialindex")

        suffix = self._get_lib_suffix()

        self.cpp_info.components["spatialindex"].set_property("cmake_target_name", "libspatialindex::spatialindex")
        self.cpp_info.components["spatialindex"].libs = ["spatialindex" + suffix]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["spatialindex"].system_libs.append("m")
        if not self.options.shared:
            libcxx = tools_legacy.stdcpp_library(self)
            if libcxx:
                self.cpp_info.components["spatialindex"].system_libs.append(libcxx)

        self.cpp_info.components["spatialindex_c"].set_property("cmake_target_name", "libspatialindex::spatialindex_c")
        self.cpp_info.components["spatialindex_c"].libs = ["spatialindex_c" + suffix]
        self.cpp_info.components["spatialindex_c"].requires = ["spatialindex"]

        if not self.options.shared and is_msvc(self):
            self.cpp_info.components["spatialindex"].defines.append("SIDX_STATIC")
            self.cpp_info.components["spatialindex_c"].defines.append("SIDX_STATIC")

    def _get_lib_suffix(self):
        suffix = ""
        if is_msvc(self):
            libs = collect_libs(self)
            for lib in libs:
                if "spatialindex_c" in lib:
                    suffix = lib.split("spatialindex_c", 1)[1]
                    break
        return suffix
