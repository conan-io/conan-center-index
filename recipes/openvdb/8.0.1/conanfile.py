import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class OpenVDBConan(ConanFile):
    name = "openvdb"
    version = "8.0.1"
    description = "OpenVDB is an open source C++ library comprising a novel hierarchical data structure and a large suite of tools for the efficient storage and manipulation of sparse volumetric data discretized on three-dimensional grids. It was developed by DreamWorks Animation for use in volumetric applications typically encountered in feature film production."
    license = "MPL-2.0"
    topics = ("conan", "openvdb")
    homepage = "https://github.com/AcademySoftwareFoundation/openvdb"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_blosc": [True, False],
        "with_zlib": [True, False],
        "with_log4cplus": [True, False],
        "with_exr": [True, False],
        "simd": ["None", "SSE42", "AVX"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_blosc": True,
        "with_zlib": True,
        "with_log4cplus": False,
        "with_exr": False,
        "simd": "None",
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
        version = str(self.settings.compiler.version)
        if version < self._compilers_min_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a %s version greater than %s" % (self.name, compiler, self._compilers_min_version[compiler]))

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 14)
        if self.settings.arch not in ("x86", "x86_64"):
            if self.options.simd != "None":
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
            self.requires("openexr/2.5.5]")
        if self.options.with_blosc:
            self.requires("c-blosc/1.20.1")
        if self.options.with_log4cplus:
            self.requires("log4cplus/2.0.5")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        # Remove FindXXX files from OpenVDB. Let Conan do the job
        tools.remove_files_by_mask(os.path.join(self._source_subfolder, "cmake"), "Find*")
        # TODO: move to patches
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "openvdb", "openvdb", "CMakeLists.txt"),
            "  find_package(IlmBase ${MINIMUM_ILMBASE_VERSION} REQUIRED)",
            "# find_package(IlmBase ${MINIMUM_ILMBASE_VERSION} REQUIRED)",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "openvdb", "openvdb", "CMakeLists.txt"),
            "  find_package(IlmBase ${MINIMUM_ILMBASE_VERSION} REQUIRED COMPONENTS Half)",
            "  find_package(OpenEXR ${MINIMUM_OPENEXR_VERSION} REQUIRED)",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "openvdb", "openvdb", "CMakeLists.txt"),
            "  get_target_property(ILMBASE_LIB_TYPE IlmBase::Half TYPE)",
            "# get_target_property(ILMBASE_LIB_TYPE IlmBase::Half TYPE)",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "openvdb", "openvdb", "CMakeLists.txt"),
            "  find_package(Blosc ${MINIMUM_BLOSC_VERSION} REQUIRED)",
            "  find_package(c-blosc ${MINIMUM_BLOSC_VERSION} REQUIRED)",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "openvdb", "openvdb", "CMakeLists.txt"),
            "  list(APPEND OPENVDB_CORE_DEPENDENT_LIBS Blosc::blosc)",
            "  list(APPEND OPENVDB_CORE_DEPENDENT_LIBS c-blosc::c-blosc)",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "openvdb", "openvdb", "CMakeLists.txt"),
            "  if(OPENEXR_USE_STATIC_LIBS OR (${ILMBASE_LIB_TYPE} STREQUAL STATIC_LIBRARY))",
            "  if(OPENEXR_USE_STATIC_LIBS)",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "openvdb", "openvdb", "CMakeLists.txt"),
            "  IlmBase::Half",
            "  OpenEXR::OpenEXR",
        )

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
