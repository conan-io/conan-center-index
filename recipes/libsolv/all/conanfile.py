import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir

required_conan_version = ">=1.53.0"


class LibSolvConan(ConanFile):
    name = "libsolv"
    description = "Library for solving packages and reading repositories"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/project/package"
    topics = ("dependency-solver", "package-repository", "packaging")

    # static build fails to find libxml2 headers
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_rpmpkg": [True, False],
        "enable_rpmmd": [True, False],
        "enable_suserepo": [True, False],
        "enable_comps": [True, False],
        "enable_helixrepo": [True, False],
        "enable_debian": [True, False],
        "enable_mdkrepo": [True, False],
        "enable_archrepo": [True, False],
        "enable_cudfrepo": [True, False],
        "enable_conda": [True, False],
        "enable_appdata": [True, False],
        "multi_semantics": [True, False],
        "enable_lzma_compression": [True, False],
        "enable_bzip2_compression": [True, False],
        "enable_zstd_compression": [True, False],
        "enable_zchunk_compression": [True, False],
        "with_libxml2": [True, False],
    }
    default_options = {
        "enable_rpmpkg": True,
        "enable_rpmmd": True,
        "enable_suserepo": True,
        "enable_comps": True,
        "enable_helixrepo": True,
        "enable_debian": True,
        "enable_mdkrepo": True,
        "enable_archrepo": True,
        "enable_cudfrepo": True,
        "enable_conda": True,
        "enable_appdata": True,
        "multi_semantics": True,
        "enable_lzma_compression": True,
        "enable_bzip2_compression": True,
        "enable_zstd_compression": True,
        "enable_zchunk_compression": True,
        "with_libxml2": True,
    }

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.enable_lzma_compression:
            self.requires("xz_utils/5.4.5")
        if self.options.enable_bzip2_compression:
            self.requires("bzip2/1.0.8")
        if self.options.enable_zstd_compression:
            self.requires("zstd/1.5.6")
        if self.options.with_libxml2:
            self.requires("libxml2/2.12.7")
        else:
            self.requires("expat/2.6.2")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.2.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_STATIC"] = not self.options.get_safe("shared", True)
        tc.variables["DISABLE_SHARED"] = not self.options.get_safe("shared", True)
        tc.variables["ENABLE_RPMPKG"] = self.options.enable_rpmpkg
        tc.variables["ENABLE_RPMMD"] = self.options.enable_rpmmd
        tc.variables["ENABLE_SUSEREPO"] = self.options.enable_suserepo
        tc.variables["ENABLE_COMPS"] = self.options.enable_comps
        tc.variables["ENABLE_HELIXREPO"] = self.options.enable_helixrepo
        tc.variables["ENABLE_DEBIAN"] = self.options.enable_debian
        tc.variables["ENABLE_MDKREPO"] = self.options.enable_mdkrepo
        tc.variables["ENABLE_ARCHREPO"] = self.options.enable_archrepo
        tc.variables["ENABLE_CUDFREPO"] = self.options.enable_cudfrepo
        tc.variables["ENABLE_CONDA"] = self.options.enable_conda
        tc.variables["ENABLE_APPDATA"] = self.options.enable_appdata
        tc.variables["MULTI_SEMANTICS"] = self.options.multi_semantics
        tc.variables["ENABLE_LZMA_COMPRESSION"] = self.options.enable_lzma_compression
        tc.variables["ENABLE_BZIP2_COMPRESSION"] = self.options.enable_bzip2_compression
        tc.variables["ENABLE_ZSTD_COMPRESSION"] = self.options.enable_zstd_compression
        tc.variables["ENABLE_ZCHUNK_COMPRESSION"] = self.options.enable_zchunk_compression
        tc.variables["WITH_LIBXML2"] = self.options.with_libxml2
        tc.variables["WITH_SYSTEM_ZCHUNK"] = False
        tc.variables["ENABLE_PERL"] = False
        tc.variables["ENABLE_PYTHON"] = False
        tc.variables["ENABLE_RUBY"] = False
        tc.variables["ENABLE_TCL"] = False
        tc.variables["ENABLE_LUA"] = False
        # Requires rpmdb
        tc.variables["ENABLE_RPMDB"] = False
        tc.variables["ENABLE_RPMDB_BYRPMHEADER"] = False
        tc.variables["ENABLE_RPMDB_LIBRPM"] = False
        tc.variables["ENABLE_RPMDB_BDB"] = False
        # Requires librpm
        tc.variables["ENABLE_RPMPKG_LIBRPM"] = False
        tc.variables["ENABLE_PUBKEY"] = False
        # Requires package/PackageInfo.h, enables CXX
        tc.variables["ENABLE_HAIKU"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("xz_utils", "cmake_file_name", "LZMA")
        deps.generate()

        VirtualBuildEnv(self).generate()

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, "${LZMA_LIBRARY}", "LibLZMA::LibLZMA")
        replace_in_file(self, cmakelists, "${EXPAT_LIBRARY}", "expat::expat")
        replace_in_file(self, cmakelists, "${LIBXML2_LIBRARIES}", "LibXml2::LibXml2")
        # Workaround for "The CMake policy CMP0091 must be NEW, but is ''"
        replace_in_file(self, cmakelists, "CMAKE_MINIMUM_REQUIRED (VERSION 2.8.5)", "CMAKE_MINIMUM_REQUIRED (VERSION 3.15)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.BSD", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "module")
        self.cpp_info.set_property("cmake_file_name", "LibSolv")
        self.cpp_info.set_property("pkg_config_name", "_libsolv_all")

        self.cpp_info.components["libsolv"].set_property("pkg_config_name", "libsolv")
        self.cpp_info.components["libsolv"].libs = ["solv"]

        self.cpp_info.components["libsolvext"].set_property("pkg_config_name", "libsolvext")
        self.cpp_info.components["libsolvext"].libs = ["solvext"]
        self.cpp_info.components["libsolvext"].requires = ["libsolv"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libsolvext"].system_libs = ["pthread"]
        self.cpp_info.components["libsolvext"].requires.append("zlib::zlib")
        if self.options.enable_lzma_compression:
            self.cpp_info.components["libsolvext"].requires.append("xz_utils::xz_utils")
        if self.options.enable_bzip2_compression:
            self.cpp_info.components["libsolvext"].requires.append("bzip2::bzip2")
        if self.options.enable_zstd_compression:
            self.cpp_info.components["libsolvext"].requires.append("zstd::zstd")
        if self.options.with_libxml2:
            self.cpp_info.components["libsolvext"].requires.append("libxml2::libxml2")
        else:
            self.cpp_info.components["libsolvext"].requires.append("expat::expat")
