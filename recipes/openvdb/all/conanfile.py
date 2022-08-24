from conan.tools.microsoft import is_msvc
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os


required_conan_version = ">=1.45.0"


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

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_min_version(self):
        return {
            "msvc": "191",
            "Visual Studio": "15",  # Should we check toolset?
            "gcc": "6.3.1",
            "clang": "3.8",
            "apple-clang": "3.8",
            "intel": "17",
        }

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.79.0")
        self.requires("onetbb/2020.3")
        self.requires("openexr/2.5.7")  # required for IlmBase::Half
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.with_exr:
            # Not necessary now. Required for IlmBase::IlmImf
            self.requires("openexr/2.5.7")
        if self.options.with_blosc:
            self.requires("c-blosc/1.21.1")
        if self.options.with_log4cplus:
            self.requires("log4cplus/2.0.7")

    def _check_compilier_version(self):
        compiler = str(self.settings.compiler)
        version = tools.Version(self.settings.compiler.version)
        minimum_version = self._compilers_min_version.get(compiler, False)
        if minimum_version and version < minimum_version:
            raise ConanInvalidConfiguration(f"{self.name} requires a {compiler} version greater than {minimum_version}")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)
        if self.settings.arch not in ("x86", "x86_64"):
            if self.options.simd:
                raise ConanInvalidConfiguration("Only intel architectures support SSE4 or AVX.")
        self._check_compilier_version()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # Remove FindXXX files from OpenVDB. Let Conan do the job
        tools.files.rm(self, os.path.join(self._source_subfolder, "cmake"), "Find*")
        with open("FindBlosc.cmake", "w") as f:
            f.write(
                """find_package(c-blosc)
if(c-blosc_FOUND)
    add_library(blosc INTERFACE)
    target_link_libraries(blosc INTERFACE c-blosc::c-blosc)
    add_library(Blosc::blosc ALIAS blosc)
endif()
"""
            )
        with open("FindIlmBase.cmake", "w") as f:
            f.write(
                """find_package(OpenEXR)
if(OpenEXR_FOUND)
  add_library(Half INTERFACE)
  add_library(IlmThread INTERFACE)
  add_library(Iex INTERFACE)
  add_library(Imath INTERFACE)
  add_library(IlmImf INTERFACE)
  target_link_libraries(Half INTERFACE OpenEXR::OpenEXR)
  target_link_libraries(IlmThread INTERFACE OpenEXR::OpenEXR)
  target_link_libraries(Iex INTERFACE OpenEXR::OpenEXR)
  target_link_libraries(Imath INTERFACE OpenEXR::OpenEXR)
  target_link_libraries(IlmImf INTERFACE OpenEXR::OpenEXR)
  add_library(IlmBase::Half ALIAS Half)
  add_library(IlmBase::IlmThread ALIAS IlmThread)
  add_library(IlmBase::Iex ALIAS Iex)
  add_library(IlmBase::Imath ALIAS Imath)
  add_library(OpenEXR::IlmImf ALIAS IlmImf)
 endif()
 """
            )

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        # exposed options
        cmake.definitions["USE_BLOSC"] = self.options.with_blosc
        cmake.definitions["USE_ZLIB"] = self.options.with_zlib
        cmake.definitions["USE_LOG4CPLUS"] = self.options.with_log4cplus
        cmake.definitions["USE_EXR"] = self.options.with_exr
        cmake.definitions["OPENVDB_SIMD"] = self.options.simd

        cmake.definitions["OPENVDB_CORE_SHARED"] = self.options.shared
        cmake.definitions["OPENVDB_CORE_STATIC"] = not self.options.shared

        # All available options but not exposed yet. Set to default values
        cmake.definitions["OPENVDB_BUILD_CORE"] = True
        cmake.definitions["OPENVDB_BUILD_BINARIES"] = False
        cmake.definitions["OPENVDB_BUILD_PYTHON_MODULE"] = False
        cmake.definitions["OPENVDB_BUILD_UNITTESTS"] = False
        cmake.definitions["OPENVDB_BUILD_DOCS"] = False
        cmake.definitions["OPENVDB_BUILD_HOUDINI_PLUGIN"] = False
        cmake.definitions["OPENVDB_BUILD_HOUDINI_ABITESTS"] = False

        cmake.definitions["OPENVDB_BUILD_AX"] = False
        cmake.definitions["OPENVDB_BUILD_AX_BINARIES"] = False
        cmake.definitions["OPENVDB_BUILD_AX_UNITTESTS"] = False

        cmake.definitions["OPENVDB_BUILD_MAYA_PLUGIN"] = False
        cmake.definitions["OPENVDB_ENABLE_RPATH"] = False
        cmake.definitions["OPENVDB_CXX_STRICT"] = False
        cmake.definitions["USE_HOUDINI"] = False
        cmake.definitions["USE_MAYA"] = False
        cmake.definitions["USE_STATIC_DEPENDENCIES"] = False
        cmake.definitions["USE_PKGCONFIG"] = False
        cmake.definitions["OPENVDB_INSTALL_CMAKE_MODULES"] = False

        cmake.definitions["Boost_USE_STATIC_LIBS"] = not self.options["boost"].shared
        cmake.definitions["OPENEXR_USE_STATIC_LIBS"] = not self.options["openexr"].shared

        cmake.definitions["OPENVDB_DISABLE_BOOST_IMPLICIT_LINKING"] = True

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "OpenVDB")
        self.cpp_info.set_property("cmake_target_name", "OpenVDB::openvdb")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        lib_prefix = "lib" if is_msvc(self) and not self.options.shared else ""
        self.cpp_info.components["openvdb-core"].libs = [lib_prefix + "openvdb"]

        lib_define = "OPENVDB_DLL" if self.options.shared else "OPENVDB_STATICLIB"
        self.cpp_info.components["openvdb-core"].defines.append(lib_define)

        if self.settings.os == "Windows":
            self.cpp_info.components["openvdb-core"].defines.append("_WIN32")
            self.cpp_info.components["openvdb-core"].defines.append("NOMINMAX")

        if not self.options["openexr"].shared:
            self.cpp_info.components["openvdb-core"].defines.append("OPENVDB_OPENEXR_STATICLIB")
        if self.options.with_exr:
            self.cpp_info.components["openvdb-core"].defines.append("OPENVDB_TOOLS_RAYTRACER_USE_EXR")
        if self.options.with_log4cplus:
            self.cpp_info.components["openvdb-core"].defines.append("OPENVDB_USE_LOG4CPLUS")

        self.cpp_info.components["openvdb-core"].requires = [
            "boost::iostreams",
            "boost::system",
            "onetbb::onetbb",
            "openexr::openexr",  # should be "openexr::Half",
        ]
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
