import os
import stat
from contextlib import contextmanager
from glob import glob
from typing import List

from conans import CMake, ConanFile, tools


class PythonOption:
    OFF = "off"
    SYSTEM = "system"
    # in future we may allow the user to specify a version when
    # libPython is available in Conan Center Index.
    ALL = [OFF, SYSTEM]
    DEFAULT = OFF


class RootConan(ConanFile):
    name = "root"
    version = "v6-22-02"
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
        # TODO: shared option should be reinstated when hooks issue is resolved
        # (see: https://github.com/conan-io/hooks/issues/252)
        # "shared": [True],
        "fPIC": [True, False],
        "python": PythonOption.ALL,
    }
    default_options = {
        # "shared": True,
        "fPIC": True,
        "libxml2:shared": True,
        "sqlite3:shared": True,
        # default python=off as there is currently no libpython in Conan center
        "python": PythonOption.OFF,
    }
    generators = ("cmake_find_package",)
    requires = (
        "opengl/system",
        "libxml2/2.9.10",
        "glu/system",
        "xorg/system",
        "sqlite3/3.33.0",
        "libjpeg/9d",
        "libpng/1.6.37",
        "libcurl/7.73.0",
        # "libuuid/1.0.3",
    )

    def configure(self):
        tools.check_min_cppstd(self, "11")

    @property
    def _rootsrcdir(self) -> str:
        version = self.version.replace("v", "")
        return f"root-{version}"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        # Patch ROOT CMake to use Conan SQLITE
        tools.replace_in_file(
            f"{self._rootsrcdir}{os.sep}CMakeLists.txt",
            "project(ROOT)",
            """project(ROOT)
            find_package(SQLite3 REQUIRED)
            set(SQLITE_INCLUDE_DIR ${SQLITE3_INCLUDE_DIRS})
            set(SQLITE_LIBRARIES SQLite::SQLite)
            """,
        )
        # Fix execute permissions on scripts
        scripts = [
            filename
            for pattern in (
                f"**{os.sep}configure",
                f"**{os.sep}*.sh",
                f"**{os.sep}*.csh",
                f"**{os.sep}*.bat",
            )
            for filename in glob(pattern, recursive=True)
        ]
        for s in scripts:
            self._make_file_executable(s)

    def _make_file_executable(self, filename):
        st = os.stat(filename)
        os.chmod(filename, st.st_mode | stat.S_IEXEC)

    @contextmanager
    def _configure_cmake(self) -> CMake:
        cmake = CMake(self)
        version = self.version.replace("v", "")
        cmakelibpath = ";".join(self.deps_cpp_info.lib_paths)
        cmakeincludepath = ";".join(self.deps_cpp_info.include_paths)
        cmake.configure(
            source_folder=f"root-{version}",
            defs={
                # TODO: Remove BUILD_SHARED_LIBS option when hooks issue is resolved
                # (see: https://github.com/conan-io/hooks/issues/252)
                "BUILD_SHARED_LIBS": "ON",
                "fail-on-missing": "ON",
                "CMAKE_CXX_STANDARD": self._CMAKE_CXX_STANDARD,
                # Prefer builtins where available
                "builtin_pcre": "ON",
                "builtin_lzma": "ON",
                "builtin_zstd": "ON",
                "builtin_xxhash": "ON",
                "builtin_lz4": "ON",
                "builtin_afterimage": "ON",
                "builtin_gsl": "ON",
                "builtin_glew": "ON",
                "builtin_gl2ps": "ON",
                "builtin_openssl": "ON",
                "builtin_fftw3": "ON",
                "builtin_cfitsio": "ON",
                "builtin_ftgl": "ON",
                "builtin_davix": "OFF",
                "builtin_tbb": "ON",
                "builtin_vdt": "ON",
                # xrootd doesn't build with builtin openssl.
                "builtin_xrootd": "OFF",
                "xrootd": "OFF",
                # No Conan packages available for these dependencies yet
                "davix": "OFF",
                "pythia6": "OFF",
                "pythia8": "OFF",
                "mysql": "OFF",
                "oracle": "OFF",
                "pgsql": "OFF",
                "gfal": "OFF",
                "tmva-pymva": "OFF",
                "pyroot": self._pyrootopt,
                "gnuinstall": "OFF",
                "soversion": "ON",
                # Tell CMake where to look for Conan provided depedencies
                "CMAKE_LIBRARY_PATH": cmakelibpath,
                "CMAKE_INCLUDE_PATH": cmakeincludepath,
                # Configure install directories
                # Conan CCI hooks restrict the allowed install directory
                # names but ROOT is very picky about where build/runtime
                # resources get installed.
                # Set install prefix to work around these limitations
                # Following: https://github.com/conan-io/conan/issues/3695
                "CMAKE_INSTALL_PREFIX": f"{self.package_folder}{os.sep}res",
            },
        )
        yield cmake

    @property
    def _CMAKE_CXX_STANDARD(self):
        compileropt = self.settings.compiler.cppstd
        if compileropt:
            return str(compileropt)
        else:
            return "11"

    @property
    def _pyrootopt(self):
        if self.options.python == PythonOption.OFF:
            return "OFF"
        else:
            return "ON"

    def build(self):
        with self._configure_cmake() as cmake:
            cmake.build()

    def package(self):
        with self._configure_cmake() as cmake:
            cmake.install()
        self.copy("LICENSE.txt", dst="licenses")
        for dir in ["include", "lib", "bin"]:
            os.symlink(
                f"{self.package_folder}{os.sep}res{os.sep}{dir}",
                f"{self.package_folder}{os.sep}{dir}",
            )
        # Fix for CMAKE-MODULES-CONFIG-FILES (KB-H016)
        for cmakefile in glob(
            f"{self.package_folder}{os.sep}res{os.sep}cmake{os.sep}*Config*.cmake"
        ):
            os.remove(cmakefile)
        # Fix for CMAKE FILE NOT IN BUILD FOLDERS (KB-H019)
        os.remove(
            f"{self.package_folder}{os.sep}res{os.sep}tutorials{os.sep}CTestCustom.cmake"
        )

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "ROOT"
        self.cpp_info.names["cmake_find_package_multi"] = "ROOT"
        # see root-config --libs for a list of libs
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
            "Tree ",
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
        self.cpp_info.builddirs = [f"res{os.sep}cmake"]
        self.cpp_info.build_modules.extend(
            [
                f"res{os.sep}cmake{os.sep}RootMacros.cmake",
                # f"res{os.sep}cmake{os.sep}ROOTUseFile.cmake",
            ]
        )
        self.cpp_info.resdirs = ["res"]

    def _fix_tbb_libs(self, libs: List[str]) -> List[str]:
        # Special treatment for tbb
        # (to handle issue https://github.com/conan-io/conan/issues/5428)
        return [(("lib" + name + ".so.2") if "tbb" in name else name) for name in libs]
