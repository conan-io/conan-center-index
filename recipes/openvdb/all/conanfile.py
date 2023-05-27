from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.microsoft import is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
import os


required_conan_version = ">=1.52.0"


class OpenVDBConan(ConanFile):
    name = "openvdb"
    description = (
        "OpenVDB is an open source C++ library comprising a novel hierarchical data"
        "structure and a large suite of tools for the efficient storage and "
        "manipulation of sparse volumetric data discretized on three-dimensional grids."
    )
    license = "MPL-2.0"
    topics = ("voxel", "voxelizer", "volume-rendering", "fx")
    homepage = "https://github.com/AcademySoftwareFoundation/openvdb"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_blosc": [True, False],
        "with_zlib": [True, False],
        "with_log4cplus": [True, False],
        "simd": [None, "SSE42", "AVX"],
        "delayed_load": [True, False],
        "nanovdb": [True, False],
        "nanovdb_with_openvdb": [True, False],
        "nanovdb_with_tbb": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_blosc": True,
        "with_zlib": True,
        "with_log4cplus": False,
        "simd": None,
        "delayed_load": True,
        "nanovdb": False,        
        "nanovdb_with_openvdb": True,
        "nanovdb_with_tbb": True,
    }

    @property
    def _has_sse_avx(self):
        return self.settings.arch in ["x86", "x86_64"]

    @property
    def _needs_boost(self):
        return True
        # Will be fixed from upstream
        # return Version(self.version) < "10.0.0" or self.options.delayed_load

    @property
    def _needs_openexr(self):
        return Version(self.version) < "8.1.0"

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _compilers_min_version(self):
        if Version(self.version) == "8.0.1":
            return {
                "msvc": "191",
                "Visual Studio": "15",  # Should we check toolset?
                "gcc": "6.3.1",
                "clang": "3.8",
                "apple-clang": "3.8",
                "intel": "17",
            }
        if Version(self.version) == "10.0.1":
            return {
                "msvc": "1928",
                "Visual Studio": "16.8.1",  # Should we check toolset?
                "gcc": "9.3.1",
                "clang": "5",
                "apple-clang": "5",
                "intel": "19",
            }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_sse_avx:
            del self.options.simd

        if Version(self.version) < "9.0.0":
            del self.options.nanovdb
            del self.options.nanovdb_with_openvdb
            del self.options.nanovdb_with_tbb

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        if Version(self.version) >= "10.0.0":
            self.tool_requires("cmake/[>=3.18.0 <4.0]")
        elif Version(self.version) >= "9.0.0":
            self.tool_requires("cmake/[>=3.15.0 <4.0]")
        else:
            self.tool_requires("cmake/[>=3.12.0 <4.0]")

    def requirements(self):
        if self._needs_boost:
            self.requires("boost/1.80.0")

        if Version(self.version) < "9.0.0":
            self.requires("onetbb/2020.3")
        else:
            self.requires("onetbb/2021.6.0")

        # Before c-blosc or openexr to avoid conflicts
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")

        if self._needs_openexr:
            self.requires("openexr/2.5.7") # required for IlmBase::Half

        if self.options.with_blosc:
            self.requires("c-blosc/1.21.1")
        if self.options.with_log4cplus:
            self.requires("log4cplus/2.0.7")

    def _check_compilier_version(self):
        compiler = str(self.settings.compiler)
        version = Version(self.settings.compiler.version)
        minimum_version = self._compilers_min_version.get(compiler, False)
        if minimum_version and version < minimum_version:
            raise ConanInvalidConfiguration(f"{self.name} requires a {compiler} version greater than {minimum_version}")

    def validate(self):
        if self.settings.compiler.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        self._check_compilier_version()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_BLOSC"] = self.options.with_blosc
        tc.variables["USE_ZLIB"] = self.options.with_zlib
        tc.variables["USE_LOG4CPLUS"] = self.options.with_log4cplus
        tc.variables["OPENVDB_SIMD"] = self.options.simd
        if Version(self.version) >= "10.0.0":
            tc.variables["OPENVDB_USE_DELAYED_LOADING"] = self.options.delayed_load

        tc.variables["OPENVDB_CORE_SHARED"] = self.options.shared
        tc.variables["OPENVDB_CORE_STATIC"] = not self.options.shared

        # All available options but not exposed yet. Set to default values
        tc.variables["OPENVDB_BUILD_CORE"] = True
        tc.variables["OPENVDB_BUILD_BINARIES"] = False
        tc.variables["USE_EXR"] = False # This is only used for vdb_render
        tc.variables["OPENVDB_BUILD_PYTHON_MODULE"] = False
        tc.variables["OPENVDB_BUILD_UNITTESTS"] = False
        tc.variables["OPENVDB_BUILD_DOCS"] = False
        tc.variables["OPENVDB_BUILD_HOUDINI_PLUGIN"] = False
        tc.variables["OPENVDB_BUILD_HOUDINI_ABITESTS"] = False

        tc.variables["OPENVDB_BUILD_AX"] = False
        tc.variables["OPENVDB_BUILD_AX_BINARIES"] = False
        tc.variables["OPENVDB_BUILD_AX_UNITTESTS"] = False

        tc.variables["OPENVDB_BUILD_MAYA_PLUGIN"] = False
        tc.variables["OPENVDB_ENABLE_RPATH"] = False
        tc.variables["OPENVDB_CXX_STRICT"] = False
        tc.variables["USE_HOUDINI"] = False
        tc.variables["USE_MAYA"] = False
        tc.variables["USE_STATIC_DEPENDENCIES"] = False
        tc.variables["USE_PKGCONFIG"] = False
        tc.variables["OPENVDB_INSTALL_CMAKE_MODULES"] = False

        if Version(self.version) >= "9.0.0":
            tc.variables["OPENVDB_BUILD_NANOVDB"] = self.options.nanovdb
            tc.variables["NANOVDB_USE_OPENVDB"] = self.options.nanovdb_with_openvdb
            tc.variables["USE_TBB"] = self.options.nanovdb_with_tbb
            tc.variables["NANOVDB_USE_INTRINSICS"] = True
            tc.variables["NANOVDB_BUILD_TOOLS"] = False

        if self._needs_boost:
            tc.variables["Boost_USE_STATIC_LIBS"] = not self.options.get_safe("boost::shared", self.options.shared)
            tc.variables["OPENVDB_DISABLE_BOOST_IMPLICIT_LINKING"] = True

        if self._needs_openexr:
            tc.variables["OPENEXR_USE_STATIC_LIBS"] = not self.options["openexr"].shared

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Create alias for Blosc target
        with open(os.path.join(self.source_folder, "cmake", "FindBlosc.cmake"), "w") as f:
            f.write(
                """find_package(c-blosc)
if(c-blosc_FOUND)
    add_library(blosc INTERFACE)
    target_link_libraries(blosc INTERFACE c-blosc::c-blosc)
    add_library(Blosc::blosc ALIAS blosc)
endif()
"""
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "OpenVDB")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        lib_prefix = "lib" if is_msvc(self) and not self.options.shared else ""
        self.cpp_info.components["openvdb-core"].libs = [lib_prefix + "openvdb"]

        lib_define = "OPENVDB_DLL" if self.options.shared else "OPENVDB_STATICLIB"
        self.cpp_info.components["openvdb-core"].defines.append(lib_define)

        if self.settings.os == "Windows":
            self.cpp_info.components["openvdb-core"].defines.append("_WIN32")
            self.cpp_info.components["openvdb-core"].defines.append("NOMINMAX")

        if self._needs_openexr and not self.options["openexr"].shared:
            self.cpp_info.components["openvdb-core"].defines.append("OPENVDB_OPENEXR_STATICLIB")
        if self.options.with_log4cplus:
            self.cpp_info.components["openvdb-core"].defines.append("OPENVDB_USE_LOG4CPLUS")

        self.cpp_info.components["openvdb-core"].requires = ["onetbb::onetbb"]

        if self._needs_boost:
            self.cpp_info.components["openvdb-core"].requires.append("boost::iostreams")
            self.cpp_info.components["openvdb-core"].requires.append("boost::system")

        if self._needs_openexr:
            self.cpp_info.components["openvdb-core"].requires.append("openexr::openexr")  # should be "openexr::Half"

        if self.settings.os == "Windows":
            self.cpp_info.components["openvdb-core"].requires.append("boost::disable_autolinking")

        if self.options.with_zlib:
            self.cpp_info.components["openvdb-core"].requires.append("zlib::zlib")
        if self.options.with_blosc:
            self.cpp_info.components["openvdb-core"].requires.append("c-blosc::c-blosc")
        if self.options.with_log4cplus:
            self.cpp_info.components["openvdb-core"].requires.append("log4cplus::log4cplus")

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["openvdb-core"].system_libs = ["pthread"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenVDB"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenVDB"
        self.cpp_info.components["openvdb-core"].names["cmake_find_package"] = "openvdb"
        self.cpp_info.components["openvdb-core"].names["cmake_find_package_multi"] = "openvdb"
        self.cpp_info.components["openvdb-core"].set_property("cmake_target_name", "OpenVDB::openvdb")


        #NanoVDB
        if Version(self.version) >= "9.0.0" and self.options.nanovdb:
            self.cpp_info.components["nanovdb"].bindirs = []
            self.cpp_info.components["nanovdb"].libdirs = []
            self.cpp_info.components["nanovdb"].requires = []
            if self.options.nanovdb_with_openvdb:
                self.cpp_info.components["nanovdb"].requires.append("openvdb-core")
            if self.options.nanovdb_with_tbb:
                self.cpp_info.components["nanovdb"].requires.append("onetbb::onetbb")
            if self.options.with_zlib:
                self.cpp_info.components["nanovdb"].requires.append("zlib::zlib")
            if self.options.with_blosc:
                self.cpp_info.components["nanovdb"].requires.append("c-blosc::c-blosc")

            if self.settings.os in ("Linux", "FreeBSD"):
                self.cpp_info.components["nanovdb"].system_libs = ["pthread"]

            self.cpp_info.components["nanovdb"].defines.append("NANOVDB_USE_INTRINSICS")

            if self.settings.os == "Windows":
                self.cpp_info.components["nanovdb"].defines.append("_USE_MATH_DEFINES")
                self.cpp_info.components["nanovdb"].defines.append("NOMINMAX")
                self.cpp_info.components["nanovdb"].defines.append("TBB_USE_PREVIEW_BINARY")

            if self.options.nanovdb_with_openvdb:
                self.cpp_info.components["nanovdb"].defines.append("NANOVDB_USE_OPENVDB")
            if self.options.nanovdb_with_tbb:
                self.cpp_info.components["nanovdb"].defines.append("NANOVDB_USE_TBB")
            if self.options.with_zlib:
                self.cpp_info.components["nanovdb"].defines.append("NANOVDB_USE_ZIP")
            if self.options.with_blosc:
                self.cpp_info.components["nanovdb"].defines.append("NANOVDB_USE_BLOSC")

            self.cpp_info.components["nanovdb"].set_property("cmake_target_name", "OpenVDB::nanovdb")
