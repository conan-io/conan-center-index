import glob
import os
import stat

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class CernRootConan(ConanFile):
    name = "cern-root"
    # version format is intentional, ROOT does not follow strict SemVer.
    # see: https://root.cern/about/versioning/
    description = "CERN ROOT data analysis framework."
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    # ROOT itself is located at: https://github.com/root-project/root
    homepage = "https://root.cern/"
    topics = ("data-analysis", "physics")

    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        # Don't allow static build as it is not supported
        # see: https://sft.its.cern.ch/jira/browse/ROOT-6446
        "fPIC": [True, False],
        # in future we may allow the user to specify a version when
        # libPython is available in Conan Center Index.
        # FIXME: add option to use CCI Python package when it is available
        "asimage": [True, False],
        "python": ["off", "system"],
    }
    default_options = {
        "fPIC": True,
        "asimage": False,  # FIXME: requires builtin_afterimage, but its build is broken
        # default python=off as there is currently no libpython in Conan center
        "python": "off",
    }
    options_description = {
        "asimage": "Enable support for image processing via libAfterImage",
        "python": "Enable support for automatic Python bindings (PyROOT)",
    }

    @property
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16.1",
            "msvc": "192",
            "gcc": "4.8",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def export_sources(self):
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("arrow/14.0.1")
        self.requires("cfitsio/4.3.0")
        self.requires("fftw/3.3.10")
        self.requires("freetype/2.13.2")
        self.requires("glew/2.2.0")
        self.requires("gsl/2.7")
        self.requires("libcurl/[>=7.78 <9]")
        self.requires("libmysqlclient/8.1.0")
        self.requires("libpq/15.4")
        self.requires("libxml2/2.11.5")
        self.requires("lz4/1.9.4")
        self.requires("odbc/2.3.11")
        self.requires("onetbb/2020.3.3")
        self.requires("opengl/system")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("pcre/8.45")
        self.requires("sqlite3/3.44.2")
        self.requires("xxhash/0.8.2")
        self.requires("xz_utils/5.4.5")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("zstd/1.5.5")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system")
            self.requires("libxft/2.3.8")
            self.requires("libxpm/3.5.13")
            self.requires("util-linux-libuuid/2.39.2")

        if self.options.asimage:
            self.requires("giflib/5.2.1")
            self.requires("libjpeg/9e")
            self.requires("libpng/1.6.40")
            self.requires("libtiff/4.6.0")

    def validate(self):
        self._enforce_minimum_compiler_version()
        self._enforce_libcxx_requirements()

    def _enforce_minimum_compiler_version(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if min_version and Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(
                f"{self.name} requires C++{self._minimum_cpp_standard} support. "
                f"The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it."
            )

    def _enforce_libcxx_requirements(self):
        libcxx = self.settings.get_safe("compiler.libcxx")
        # ROOT doesn't currently build with libc++.
        # This restriction may be lifted in future if the problems are fixed upstream
        if libcxx and libcxx == "libc++":
            raise ConanInvalidConfiguration(f'{self.name} is incompatible with libc++".')

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @staticmethod
    def _make_file_executable(filename):
        st = os.stat(filename)
        os.chmod(filename, st.st_mode | stat.S_IEXEC)

    def generate(self):
        tc = CMakeToolchain(self)
        # Configure build options found at
        # https://github.com/root-project/root/blob/v6-22-06/cmake/modules/RootBuildOptions.cmake#L80-L193
        tc.variables["CMAKE_CXX_STANDARD"] = self._cmake_cxx_standard
        tc.variables["BUILD_SHARED_LIBS"] = True
        tc.variables["shared"] = True
        tc.variables["asimage"] = self.options.asimage
        tc.variables["fail-on-missing"] = True
        tc.variables["soversion"] = True
        tc.variables["x11"] = self.settings.os in ["Linux", "FreeBSD"]
        # Disable builtins and use Conan deps where available
        tc.variables["builtin_cfitsio"] = False
        tc.variables["builtin_davix"] = False
        tc.variables["builtin_fftw3"] = False
        tc.variables["builtin_freetype"] = False
        tc.variables["builtin_glew"] = False
        tc.variables["builtin_gsl"] = False
        tc.variables["builtin_lz4"] = False
        tc.variables["builtin_lzma"] = False
        tc.variables["builtin_openssl"] = False
        tc.variables["builtin_pcre"] = False
        tc.variables["builtin_tbb"] = False
        tc.variables["builtin_xxhash"] = False
        tc.variables["builtin_zlib"] = False
        tc.variables["builtin_zstd"] = False
        # Enable builtins where there is no Conan package
        tc.variables["builtin_afterimage"] = self.options.asimage  # FIXME : replace with afterimage CCI package when available
        tc.variables["builtin_gl2ps"] = True  # FIXME : replace with gl2ps CCI package when available
        tc.variables["builtin_ftgl"] = True  # FIXME : replace with ftgl CCI package when available
        tc.variables["builtin_vdt"] = True  # FIXME : replace with vdt CCI package when available
        tc.variables["builtin_clang"] = True
        tc.variables["builtin_llvm"] = True
        # Enable optional dependencies
        tc.variables["arrow"] = True
        tc.variables["mysql"] = True
        tc.variables["odbc"] = True
        tc.variables["pgsql"] = True
        # No Conan packages available for these dependencies yet
        tc.variables["davix"] = False  # FIXME : switch on if davix CCI package available
        tc.variables["pythia6"] = False  # FIXME : switch on if pythia6 CCI package available
        tc.variables["pythia8"] = False  # FIXME : switch on if pythia8 CCI package available
        tc.variables["oracle"] = False
        tc.variables["gfal"] = False  # FIXME: switch on if gfal CCI package available
        tc.variables["tmva-pymva"] = False  # FIXME: switch on if Python CCI package available
        tc.variables["xrootd"] = False  # FIXME: switch on if xrootd CCI package available
        tc.variables["pyroot"] = self._cmake_pyrootopt
        # clad is built with ExternalProject_Add and its
        # COMPILE_DEFINITIONS property is not propagated causing the build to
        # fail on some systems if libcxx != libstdc++11
        tc.variables["clad"] = False
        # Configure install directories
        # Conan CCI hooks restrict the allowed install directory
        # names but ROOT is very picky about where build/runtime
        # resources get installed.
        # Set install prefix to work around these limitations
        # Following: https://github.com/conan-io/conan/issues/3695
        tc.variables["CMAKE_INSTALL_CMAKEDIR"] = "lib/cmake"
        tc.variables["CMAKE_INSTALL_DATAROOTDIR"] = "res/share"
        tc.variables["CMAKE_INSTALL_SYSCONFDIR"] = "res/etc"
        tc.generate()

        cmake_pkgs = {
            "arrow": "Arrow",
            "cfitsio": "CFITSIO",
            "fftw": "FFTW",
            "freetype": "Freetype",
            "giflib": "GIF",
            "glew": "GLEW",
            "gsl": "GSL",
            "libcurl": "CURL",
            "libjpeg": "JPEG",
            "libmysqlclient": "MySQL",
            "libpng": "PNG",
            "libpq": "PostgreSQL",
            "libxml2": "LibXml2",
            "libxft": "X11_Xft",
            "libxpm": "X11_Xpm",
            "lz4": "LZ4",
            "odbc": "ODBC",
            "onetbb": "TBB",
            "openssl": "OpenSSL",
            "pcre": "PCRE",
            "sqlite3": "Sqlite",
            "tiff": "TIFF",
            "xxhash": "xxHash",
            "xz_utils": "LibLZMA",
            "zlib": "ZLIB",
            "zstd": "ZSTD",
            # "afterimage": "AfterImage",
            # "alien": "Alien",
            # "blas": "BLAS",
            # "cuda": "CUDA",
            # "cudnn": "CuDNN",
            # "davix": "Davix",
            # "dcap": "DCAP",
            # "fastcgi": "FastCGI",
            # "ftgl": "FTGL",
            # "gfal": "GFAL",
            # "gl2ps": "gl2ps",
            # "graphviz": "Graphviz",
            # "jemalloc": "jemalloc",
            # "monalisa": "Monalisa",
            # "mpi": "MPI",
            # "oracle": "Oracle",
            # "pythia6": "Pythia6",
            # "pythia8": "Pythia8",
            # "r": "R",
            # "tcmalloc": "tcmalloc",
            # "unuran": "Unuran",
            # "vc": "Vc",
            # "vdt": "Vdt",
            # "veccore": "VecCore",
            # "vecgeom": "VecGeom",
            # "xrootd": "XROOTD",
        }

        tc = CMakeDeps(self)
        for package, cmake_name in cmake_pkgs.items():
            tc.set_property(package, "cmake_file_name", cmake_name)
        tc.set_property("freetype", "cmake_target_name", "FreeType::FreeType")
        tc.set_property("pcre", "cmake_target_name", "PCRE::PCRE")
        tc.set_property("xxhash", "cmake_target_name", "xxHash::xxHash")
        tc.set_property("lz4", "cmake_target_name", "LZ4::LZ4")
        tc.generate()

    def _patch_source_cmake(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
            "set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake/modules)",
            "list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake/modules)")

    def _fix_source_permissions(self):
        # Fix execute permissions on scripts
        for pattern in [
            os.path.join(self.source_folder, "**", "configure"),
            os.path.join(self.source_folder, "**", "*.sh"),
            os.path.join(self.source_folder, "**", "*.csh"),
            os.path.join(self.source_folder, "**", "*.bat"),
        ]:
            for filename in glob.glob(os.path.join(self.source_folder, pattern), recursive=True):
                self._make_file_executable(filename)

    def _patch_sources(self):
        apply_conandata_patches(self)
        self._patch_source_cmake()
        self._fix_source_permissions()
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "project(ROOT)", "project(ROOT)\n\ninclude(conan_deps.cmake)")

    @property
    def _cmake_cxx_standard(self):
        return str(self.settings.get_safe("compiler.cppstd", self._minimum_cpp_standard))

    @property
    def _cmake_pyrootopt(self):
        return self.options.python != "off"

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # Fix for CMAKE-MODULES-CONFIG-FILES (KB-H016)
        rm(self, "*Config*.cmake", os.path.join(self.package_folder, "lib", "cmake"), recursive=True)
        rmdir(self, os.path.join(self.package_folder, "res", "README"))
        rmdir(self, os.path.join(self.package_folder, "res", "share", "man"))
        rmdir(self, os.path.join(self.package_folder, "res", "share", "doc"))
        rmdir(self, os.path.join(self.package_folder, "res", "tutorials"))

    def package_info(self):
        # FIXME: ROOT generates multiple CMake files
        self.cpp_info.set_property("cmake_file_name", "ROOT")
        self.cpp_info.set_property("cmake_target_name", "ROOT::ROOT")

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
        self.cpp_info.resdirs = ["res"]

        build_modules = [
            os.path.join("lib", "cmake", "RootMacros.cmake"),
            # os.path.join("lib", "cmake", "ROOTUseFile.cmake"),
        ]
        self.cpp_info.set_property("cmake_build_modules", build_modules)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "ROOT"
        self.cpp_info.names["cmake_find_package_multi"] = "ROOT"
        self.cpp_info.builddirs = [os.path.join("lib", "cmake")]
        self.cpp_info.build_modules["cmake_find_package"] = build_modules
        self.cpp_info.build_modules["cmake_find_package_multi"] = build_modules
