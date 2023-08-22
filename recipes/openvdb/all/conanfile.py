import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class OpenVDBConan(ConanFile):
    name = "openvdb"
    description = (
        "OpenVDB is an open source C++ library comprising a novel hierarchical data"
        "structure and a large suite of tools for the efficient storage and "
        "manipulation of sparse volumetric data discretized on three-dimensional grids."
    )
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AcademySoftwareFoundation/openvdb"
    topics = ("voxel", "voxelizer", "volume-rendering", "fx", "vdb")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_blosc": [True, False],
        "with_zlib": [True, False],
        "with_log4cplus": [True, False],
        "with_exr": [True, False],
        "simd": [None, "SSE42", "AVX"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_blosc": True,
        "with_zlib": True,
        "with_log4cplus": False,
        "with_exr": False,
        "simd": None,
    }

    @property
    def _compilers_min_version(self):
        return {
            "msvc": "191",
            "Visual Studio": "15",  # Should we check toolset?
            "gcc": "6.3.1",
            "clang": "3.8",
            "apple-clang": "3.8",
            "intel-cc": "17",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.83.0", transitive_headers=True)
        # onetbb/2021.x fails with "'tbb::split' has not been declared"
        self.requires("onetbb/2020.3.3", transitive_headers=True)
        # required for IlmBase::Half even if with_exr is not enabled
        if Version(self.version) >= "8.2.0":
            self.requires("openexr/3.1.9", transitive_headers=True)
        else:
            self.requires("openexr/2.5.7", transitive_headers=True)
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_blosc:
            self.requires("c-blosc/1.21.4")
        if self.options.with_log4cplus:
            self.requires("log4cplus/2.1.0", transitive_headers=True)

    def _check_compilier_version(self):
        compiler = str(self.settings.compiler)
        version = Version(self.settings.compiler.version)
        minimum_version = self._compilers_min_version.get(compiler, False)
        if minimum_version and version < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name} requires a {compiler} version greater than {minimum_version}"
            )

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)
        if self.settings.arch not in ("x86", "x86_64"):
            if self.options.simd:
                raise ConanInvalidConfiguration("Only intel architectures support SSE4 or AVX.")
        self._check_compilier_version()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # exposed options
        tc.cache_variables["USE_BLOSC"] = self.options.with_blosc
        tc.cache_variables["USE_ZLIB"] = self.options.with_zlib
        tc.cache_variables["USE_LOG4CPLUS"] = self.options.with_log4cplus
        tc.cache_variables["USE_EXR"] = self.options.with_exr
        tc.cache_variables["OPENVDB_SIMD"] = self.options.simd

        tc.cache_variables["OPENVDB_CORE_SHARED"] = self.options.shared
        tc.cache_variables["OPENVDB_CORE_STATIC"] = not self.options.shared

        # All available options but not exposed yet. Set to default values
        tc.cache_variables["OPENVDB_BUILD_CORE"] = True
        tc.cache_variables["OPENVDB_BUILD_BINARIES"] = False
        tc.cache_variables["OPENVDB_BUILD_PYTHON_MODULE"] = False
        tc.cache_variables["OPENVDB_BUILD_UNITTESTS"] = False
        tc.cache_variables["OPENVDB_BUILD_DOCS"] = False
        tc.cache_variables["OPENVDB_BUILD_HOUDINI_PLUGIN"] = False
        tc.cache_variables["OPENVDB_BUILD_HOUDINI_ABITESTS"] = False

        tc.cache_variables["OPENVDB_BUILD_AX"] = False
        tc.cache_variables["OPENVDB_BUILD_AX_BINARIES"] = False
        tc.cache_variables["OPENVDB_BUILD_AX_UNITTESTS"] = False

        tc.cache_variables["OPENVDB_BUILD_MAYA_PLUGIN"] = False
        tc.cache_variables["OPENVDB_ENABLE_RPATH"] = False
        tc.cache_variables["OPENVDB_CXX_STRICT"] = False
        tc.cache_variables["USE_HOUDINI"] = False
        tc.cache_variables["USE_MAYA"] = False
        tc.cache_variables["USE_STATIC_DEPENDENCIES"] = False
        tc.cache_variables["USE_PKGCONFIG"] = False
        tc.cache_variables["OPENVDB_INSTALL_CMAKE_MODULES"] = False

        tc.cache_variables["Boost_USE_STATIC_LIBS"] = not self.dependencies["boost"].options.shared
        tc.cache_variables["OPENEXR_USE_STATIC_LIBS"] = not self.dependencies["openexr"].options.shared

        tc.cache_variables["OPENVDB_DISABLE_BOOST_IMPLICIT_LINKING"] = True

        tc.cache_variables["OPENVDB_FUTURE_DEPRECATION"] = False

        tc.generate()

        tc = CMakeDeps(self)
        tc.set_property("c-blosc", "cmake_file_name", "Blosc")
        tc.set_property("c-blosc", "cmake_target_name", "Blosc::blosc")
        tc.set_property("openexr", "cmake_file_name", "IlmBase")
        tc.generate()

    def _patch_sources(self):
        # Remove FindXXX files from OpenVDB. Let Conan do the job
        rm(self, "Find*.cmake", os.path.join(self.source_folder, "cmake"), recursive=True)
        replace_in_file(self, os.path.join(self.source_folder, "openvdb", "openvdb", "CMakeLists.txt"),
                        "${MINIMUM_TBB_VERSION}", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "OpenVDB")
        self.cpp_info.set_property("cmake_target_name", "OpenVDB::openvdb")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        lib_prefix = "lib" if is_msvc(self) and not self.options.shared else ""
        main_component = self.cpp_info.components["openvdb-core"]
        main_component.libs = [lib_prefix + "openvdb"]

        lib_define = "OPENVDB_DLL" if self.options.shared else "OPENVDB_STATICLIB"
        main_component.defines.append(lib_define)

        if self.settings.os == "Windows":
            main_component.defines.append("_WIN32")
            main_component.defines.append("NOMINMAX")

        if not self.dependencies["openexr"].options.shared:
            main_component.defines.append("OPENVDB_OPENEXR_STATICLIB")
        if self.options.with_exr:
            main_component.defines.append("OPENVDB_TOOLS_RAYTRACER_USE_EXR")
        if self.options.with_log4cplus:
            main_component.defines.append("OPENVDB_USE_LOG4CPLUS")

        main_component.requires = [
            "boost::iostreams",
            "boost::system",
            "onetbb::onetbb",
            "openexr::openexr",  # should be "openexr::Half",
        ]
        if self.settings.os == "Windows":
            main_component.requires.append("boost::disable_autolinking")

        if self.options.with_zlib:
            main_component.requires.append("zlib::zlib")
        if self.options.with_blosc:
            main_component.requires.append("c-blosc::c-blosc")
        if self.options.with_log4cplus:
            main_component.requires.append("log4cplus::log4cplus")

        if self.settings.os in ("Linux", "FreeBSD"):
            main_component.system_libs = ["pthread"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenVDB"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenVDB"
        main_component.names["cmake_find_package"] = "openvdb"
        main_component.names["cmake_find_package_multi"] = "openvdb"
        main_component.set_property("cmake_target_name", "OpenVDB::openvdb")
