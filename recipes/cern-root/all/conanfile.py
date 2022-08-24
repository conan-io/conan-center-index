from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import glob
import os
import shutil
import stat
import textwrap


class PythonOption:
    OFF = "off"
    SYSTEM = "system"
    # in future we may allow the user to specify a version when
    # libPython is available in Conan Center Index.
    # FIXME: add option to use CCI Python package when it is available
    ALL = [OFF, SYSTEM]


required_conan_version = ">=1.33.0"


class CernRootConan(ConanFile):
    name = "cern-root"
    # version format is intentional, ROOT does not follow strict SemVer.
    # see: https://root.cern/about/versioning/
    license = "LGPL-2.1-or-later"  # of ROOT itself, the recipe is under MIT license.
    homepage = "https://root.cern/"
    # ROOT itself is located at: https://github.com/root-project/root
    url = "https://github.com/conan-io/conan-center-index"
    description = "CERN ROOT data analysis framework."
    topics = ("data-analysis", "physics")
    settings = ("os", "compiler", "build_type", "arch")
    options = {
        # Don't allow static build as it is not supported
        # see: https://sft.its.cern.ch/jira/browse/ROOT-6446
        # FIXME: shared option should be reinstated when hooks issue is resolved
        # (see: https://github.com/conan-io/hooks/issues/252)
        # "shared": [True],
        "fPIC": [True, False],
        "python": PythonOption.ALL,
    }
    default_options = {
        # "shared": True,
        "fPIC": True,
        # default python=off as there is currently no libpython in Conan center
        "python": PythonOption.OFF,
    }

    exports_sources = "patches/*"
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16.1",
            "gcc": "4.8",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("cfitsio/4.0.0")
        self.requires("fftw/3.3.9")
        self.requires("giflib/5.2.1")
        self.requires("glew/2.2.0")
        self.requires("glu/system")
        self.requires("libcurl/7.78.0")
        self.requires("libjpeg/9d")
        self.requires("libpng/1.6.37")
        self.requires("libxml2/2.9.12")
        self.requires("lz4/1.9.3")
        self.requires("opengl/system")
        self.requires("openssl/1.1.1l")
        self.requires("pcre/8.44")
        self.requires("sqlite3/3.36.0")
        self.requires("tbb/2020.3")
        self.requires("xorg/system")
        self.requires("xxhash/0.8.0")
        self.requires("xz_utils/5.2.5")
        self.requires("zstd/1.5.0")

    def validate(self):
        self._enforce_minimum_compiler_version()
        self._enforce_libcxx_requirements()

    def _enforce_minimum_compiler_version(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn(
                "{} recipe lacks information about the {} compiler support.".format(
                    self.name, self.settings.compiler
                )
            )
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++{} support. The current compiler {} {} does not support it.".format(
                        self.name,
                        self._minimum_cpp_standard,
                        self.settings.compiler,
                        self.settings.compiler.version,
                    )
                )

    def _enforce_libcxx_requirements(self):
        compiler = self.settings.compiler
        libcxx = compiler.get_safe("libcxx")
        # ROOT doesn't currently build with libc++.
        # This restriction may be lifted in future if the problems are fixed upstream
        if libcxx and libcxx == "libc++":
            raise ConanInvalidConfiguration(
                '{} is incompatible with libc++".'.format(self.name)
            )

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_source_cmake(self):
        try:
            os.remove(os.path.join(self._source_subfolder, "cmake", "modules", "FindTBB.cmake"))
        except OSError:
            pass
        # Conan generated cmake_find_packages names differ from
        # names ROOT expects (usually only due to case differences)
        # There is currently no way to change these names
        # see: https://github.com/conan-io/conan/issues/4430
        # Patch ROOT CMake to use Conan dependencies
        tools.files.replace_in_file(self, 
            os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"),
            "project(ROOT)",
            textwrap.dedent("""\
                    project(ROOT)
                    # sets the current C runtime on MSVC (MT vs MD vd MTd vs MDd)
                    include("{install_folder}/conanbuildinfo.cmake")
                    conan_basic_setup(NO_OUTPUT_DIRS)
                    find_package(OpenSSL REQUIRED)
                    set(OPENSSL_VERSION ${{OpenSSL_VERSION}})
                    find_package(LibXml2 REQUIRED)
                    set(LIBXML2_INCLUDE_DIR ${{LibXml2_INCLUDE_DIR}})
                    set(LIBXML2_LIBRARIES ${{LibXml2_LIBRARIES}})
                    find_package(SQLite3 REQUIRED)
                    set(SQLITE_INCLUDE_DIR ${{SQLITE3_INCLUDE_DIRS}})
                    set(SQLITE_LIBRARIES SQLite::SQLite3)
            """).format(install_folder=self.install_folder.replace("\\", "/"))
        )
        tools.files.replace_in_file(self, os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"),
                              "set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake/modules)",
                              "list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake/modules)")

    def _fix_source_permissions(self):
        # Fix execute permissions on scripts
        scripts = [
            filename
            for pattern in (
                os.path.join("**", "configure"),
                os.path.join("**", "*.sh"),
                os.path.join("**", "*.csh"),
                os.path.join("**", "*.bat"),
            )
            for filename in glob.glob(os.path.join(self.source_folder, pattern), recursive=True)
        ]
        for s in scripts:
            self._make_file_executable(s)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        self._patch_source_cmake()
        self._fix_source_permissions()

    @staticmethod
    def _make_file_executable(filename):
        st = os.stat(filename)
        os.chmod(filename, st.st_mode | stat.S_IEXEC)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        cmakelibpath = ";".join(self.deps_cpp_info.lib_paths)
        cmakeincludepath = ";".join(self.deps_cpp_info.include_paths)
        self._cmake.definitions.update({
            "BUILD_SHARED_LIBS": True,
            "fail-on-missing": True,
            "CMAKE_CXX_STANDARD": self._cmake_cxx_standard,
            "gnuinstall": True,
            "soversion": True,
            # Disable builtins and use Conan deps where available
            "builtin_cfitsio": False,
            "builtin_davix": False,
            "builtin_fftw3": False,
            "builtin_freetype": False,
            "builtin_glew": False,
            "builtin_lz4": False,
            "builtin_lzma": False,
            "builtin_openssl": False,
            "builtin_pcre": False,
            "builtin_tbb": False,
            "builtin_xxhash": False,
            "builtin_zlib": False,
            "builtin_zstd": False,
            # Enable builtins where there is no Conan package
            "builtin_afterimage": True,  # FIXME : replace with afterimage CCI package when available
            "builtin_gsl": True,  # FIXME : replace with gsl CCI package when available
            "builtin_gl2ps": True,  # FIXME : replace with gl2ps CCI package when available
            "builtin_ftgl": True,  # FIXME : replace with ftgl CCI package when available
            "builtin_vdt": True,  # FIXME : replace with vdt CCI package when available
            # No Conan packages available for these dependencies yet
            "davix": False,  # FIXME : switch on if davix CCI package available
            "pythia6": False,  # FIXME : switch on if pythia6 CCI package available
            "pythia8": False,  # FIXME : switch on if pythia8 CCI package available
            "mysql": False,  # FIXME : switch on if mysql CCI package available
            "oracle": False,
            "pgsql": False,  # FIXME: switch on if PostgreSQL CCI package available
            "gfal": False,  # FIXME: switch on if gfal CCI package available
            "tmva-pymva": False,  # FIXME: switch on if Python CCI package available
            "xrootd": False,  # FIXME: switch on if xrootd CCI package available
            "pyroot": self._cmake_pyrootopt,
            # clad is built with ExternalProject_Add and its
            # COMPILE_DEFINITIONS property is not propagated causing the build to
            # fail on some systems if libcxx != libstdc++11
            "clad": False,
            # Tell CMake where to look for Conan provided depedencies
            "CMAKE_LIBRARY_PATH": cmakelibpath.replace("\\", "/"),
            "CMAKE_INCLUDE_PATH": cmakeincludepath.replace("\\", "/"),
            # Configure install directories
            # Conan CCI hooks restrict the allowed install directory
            # names but ROOT is very picky about where build/runtime
            # resources get installed.
            # Set install prefix to work around these limitations
            # Following: https://github.com/conan-io/conan/issues/3695
            "CMAKE_INSTALL_CMAKEDIR": "lib/cmake",
            "CMAKE_INSTALL_DATAROOTDIR": "res/share",
            "CMAKE_INSTALL_SYSCONFDIR": "res/etc",
            # Fix some Conan-ROOT CMake variable naming differences
            "PNG_PNG_INCLUDE_DIR": ";".join(self.deps_cpp_info["libpng"].include_paths).replace("\\", "/"),
            "LIBLZMA_INCLUDE_DIR": ";".join(self.deps_cpp_info["xz_utils"].include_paths).replace("\\", "/"),
        })
        self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def _move_findcmake_conan_to_root_dir(self):
        for f in ["opengl_system", "GLEW", "glu", "TBB", "LibXml2", "ZLIB", "SQLite3"]:
            shutil.copy(
                "Find{}.cmake".format(f),
                os.path.join(
                    self.source_folder, self._source_subfolder, "cmake", "modules"
                ),
            )

    @property
    def _cmake_cxx_standard(self):
        return str(self.settings.compiler.get_safe("cppstd", "11"))

    @property
    def _cmake_pyrootopt(self):
        if self.options.python == PythonOption.OFF:
            return False
        else:
            return True

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        # Fix for CMAKE-MODULES-CONFIG-FILES (KB-H016)
        tools.files.rm(self, os.path.join(self.package_folder, "lib", "cmake"), "*Config*.cmake")
        tools.files.rmdir(self, os.path.join(self.package_folder, "res", "README"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "res", "share", "man"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "res", "share", "doc"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "res", "tutorials"))

    def package_info(self):
        # FIXME: ROOT generates multiple CMake files
        self.cpp_info.names["cmake_find_package"] = "ROOT"
        self.cpp_info.names["cmake_find_package_multi"] = "ROOT"
        # See root-config --libs for a list of ordered libs
        self.cpp_info.libs = [
            "Core",
            "Imt",
            "RIO",
            "Net",
            "Hist",
            "Graf",
            "Graf3d",
            "Gpad",
            "ROOTVecOps",
            "Tree",
            "TreePlayer",
            "Rint",
            "Postscript",
            "Matrix",
            "Physics",
            "MathCore",
            "Thread",
            "MultiProc",
            "ROOTDataFrame",
        ]
        self.cpp_info.builddirs = [os.path.join("lib", "cmake")]
        self.cpp_info.build_modules.extend(
            [
                os.path.join("lib", "cmake", "RootMacros.cmake"),
                # os.path.join("lib", "cmake", "ROOTUseFile.cmake"),
            ]
        )
        self.cpp_info.resdirs = ["res"]
