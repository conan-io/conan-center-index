import glob
import os
import shutil
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
        "python": ["off", "system"],
    }
    default_options = {
        "fPIC": True,
        # default python=off as there is currently no libpython in Conan center
        "python": "off",
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
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cfitsio/4.3.0")
        self.requires("fftw/3.3.10")
        self.requires("giflib/5.2.1")
        self.requires("glew/2.2.0")
        self.requires("glu/system")
        self.requires("libcurl/[>=7.78 <9]")
        self.requires("libjpeg/9e")
        self.requires("libpng/1.6.40")
        self.requires("libxml2/2.11.5")
        self.requires("lz4/1.9.4")
        self.requires("opengl/system")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("pcre/8.45")
        self.requires("sqlite3/3.44.0")
        self.requires("onetbb/2021.10.0")
        self.requires("xorg/system")
        self.requires("xxhash/0.8.2")
        self.requires("xz_utils/5.4.4")
        self.requires("zstd/1.5.5")

    def validate(self):
        self._enforce_minimum_compiler_version()
        self._enforce_libcxx_requirements()

    def _enforce_minimum_compiler_version(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warning(
                f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support."
            )
        else:
            if Version(self.settings.compiler.version) < min_version:
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
        tc.variables["BUILD_SHARED_LIBS"] = True
        tc.variables["fail-on-missing"] = True
        tc.variables["CMAKE_CXX_STANDARD"] = self._cmake_cxx_standard
        tc.variables["gnuinstall"] = True
        tc.variables["soversion"] = True
        # Disable builtins and use Conan deps where available
        tc.variables["builtin_cfitsio"] = False
        tc.variables["builtin_davix"] = False
        tc.variables["builtin_fftw3"] = False
        tc.variables["builtin_freetype"] = False
        tc.variables["builtin_glew"] = False
        tc.variables["builtin_lz4"] = False
        tc.variables["builtin_lzma"] = False
        tc.variables["builtin_openssl"] = False
        tc.variables["builtin_pcre"] = False
        tc.variables["builtin_tbb"] = False
        tc.variables["builtin_xxhash"] = False
        tc.variables["builtin_zlib"] = False
        tc.variables["builtin_zstd"] = False
        # Enable builtins where there is no Conan package
        tc.variables["builtin_afterimage"] = True  # FIXME : replace with afterimage CCI package when available
        tc.variables["builtin_gsl"] = True  # FIXME : replace with gsl CCI package when available
        tc.variables["builtin_gl2ps"] = True  # FIXME : replace with gl2ps CCI package when available
        tc.variables["builtin_ftgl"] = True  # FIXME : replace with ftgl CCI package when available
        tc.variables["builtin_vdt"] = True  # FIXME : replace with vdt CCI package when available
        # No Conan packages available for these dependencies yet
        tc.variables["davix"] = False  # FIXME : switch on if davix CCI package available
        tc.variables["pythia6"] = False  # FIXME : switch on if pythia6 CCI package available
        tc.variables["pythia8"] = False  # FIXME : switch on if pythia8 CCI package available
        tc.variables["mysql"] = False  # FIXME : switch on if mysql CCI package available
        tc.variables["oracle"] = False
        tc.variables["pgsql"] = False  # FIXME: switch on if PostgreSQL CCI package available
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

        tc = CMakeDeps(self)
        tc.set_property("pcre", "cmake_target_name", "PCRE::PCRE")
        tc.set_property("xxhash", "cmake_target_name", "xxHash::xxHash")
        tc.set_property("lz4", "cmake_target_name", "LZ4::LZ4")
        tc.generate()

    def _patch_source_cmake(self):
        rm(self, "FindTBB.cmake", os.path.join(self.source_folder, "cmake", "modules"))
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

    def _move_findcmake_conan_to_root_dir(self):
        for f in ["opengl_system", "GLEW", "glu", "TBB", "LibXml2", "ZLIB", "SQLite3"]:
            shutil.copy(f"Find{f}.cmake", os.path.join(self.source_folder, "cmake", "modules"))

    @property
    def _cmake_cxx_standard(self):
        return str(self.settings.get_safe("compiler.cppstd", "11"))

    @property
    def _cmake_pyrootopt(self):
        return self.options.python != "off"

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
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
