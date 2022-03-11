import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


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
    exports_sources = ["CMakeLists.txt", "patches/*.patch"]
    generators = "cmake", "cmake_find_package"
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

    _cmake = None

    _compilers_min_version = {
        "msvc": "19.10",
        "Visual Studio": "15",  # Should we check toolset?
        "gcc": "6.3.1",
        "clang": "3.8",
        "apple-clang": "3.8",
        "intel": "17",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _check_compilier_version(self):
        compiler = str(self.settings.compiler)
        version = tools.Version(self.settings.compiler.version)
        if version < self._compilers_min_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a %s version greater than %s" % (self.name, compiler, self._compilers_min_version[compiler]))

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 14)
        if self.settings.arch not in ("x86", "x86_64"):
            if self.options.simd:
                raise ConanInvalidConfiguration("Only intel architectures support SSE4 or AVX.")
        self._check_compilier_version()

    def requirements(self):
        self.requires("boost/1.75.0")
        self.requires("tbb/2020.3")
        self.requires("openexr/2.5.5")  # required for IlmBase::Half
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")
        if self.options.with_exr:
            # Not necessary now. Required for IlmBase::IlmImf
            self.requires("openexr/2.5.5")
        if self.options.with_blosc:
            self.requires("c-blosc/1.20.1")
        if self.options.with_log4cplus:
            self.requires("log4cplus/2.0.5")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        # Remove FindXXX files from OpenVDB. Let Conan do the job
        tools.remove_files_by_mask(os.path.join(self._source_subfolder, "cmake"), "Find*")
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
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        # exposed options
        self._cmake.definitions["USE_BLOSC"] = self.options.with_blosc
        self._cmake.definitions["USE_ZLIB"] = self.options.with_zlib
        self._cmake.definitions["USE_LOG4CPLUS"] = self.options.with_log4cplus
        self._cmake.definitions["USE_EXR"] = self.options.with_exr
        self._cmake.definitions["OPENVDB_SIMD"] = self.options.simd

        self._cmake.definitions["OPENVDB_CORE_SHARED"] = self.options.shared
        self._cmake.definitions["OPENVDB_CORE_STATIC"] = not self.options.shared

        # All available options but not exposed yet. Set to default values
        self._cmake.definitions["OPENVDB_BUILD_CORE"] = True
        self._cmake.definitions["OPENVDB_BUILD_BINARIES"] = False
        self._cmake.definitions["OPENVDB_BUILD_PYTHON_MODULE"] = False
        self._cmake.definitions["OPENVDB_BUILD_UNITTESTS"] = False
        self._cmake.definitions["OPENVDB_BUILD_DOCS"] = False
        self._cmake.definitions["OPENVDB_BUILD_HOUDINI_PLUGIN"] = False
        self._cmake.definitions["OPENVDB_BUILD_HOUDINI_ABITESTS"] = False

        self._cmake.definitions["OPENVDB_BUILD_AX"] = False
        self._cmake.definitions["OPENVDB_BUILD_AX_BINARIES"] = False
        self._cmake.definitions["OPENVDB_BUILD_AX_UNITTESTS"] = False

        self._cmake.definitions["OPENVDB_BUILD_MAYA_PLUGIN"] = False
        self._cmake.definitions["OPENVDB_ENABLE_RPATH"] = False
        self._cmake.definitions["OPENVDB_CXX_STRICT"] = False
        self._cmake.definitions["USE_HOUDINI"] = False
        self._cmake.definitions["USE_MAYA"] = False
        self._cmake.definitions["USE_STATIC_DEPENDENCIES"] = False
        self._cmake.definitions["USE_PKGCONFIG"] = False
        self._cmake.definitions["OPENVDB_INSTALL_CMAKE_MODULES"] = False

        self._cmake.definitions["Boost_USE_STATIC_LIBS"] = not self.options["boost"].shared
        self._cmake.definitions["OPENEXR_USE_STATIC_LIBS"] = not self.options["openexr"].shared

        self._cmake.definitions["OPENVDB_DISABLE_BOOST_IMPLICIT_LINKING"] = True

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "OpenVDB"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenVDB"

        target_suffix = "_shared" if self.options.shared else "_static"
        lib_prefix = "" if self.options.shared or self.settings.os != "Windows" else "lib"
        self.cpp_info.components["openvdb-core"].names["cmake_find_package"] = "openvdb" + target_suffix
        self.cpp_info.components["openvdb-core"].names["cmake_find_package_multi"] = "openvdb" + target_suffix

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
            "tbb::tbb",
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
