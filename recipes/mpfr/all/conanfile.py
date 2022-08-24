from conans import ConanFile, AutoToolsBuildEnvironment, CMake, tools
from conans.errors import ConanException
import contextlib
import os
import re
import shlex

required_conan_version = ">=1.33.0"


class MpfrConan(ConanFile):
    name = "mpfr"
    description = "The MPFR library is a C library for multiple-precision floating-point computations with " \
                  "correct rounding"
    topics = ("mpfr", "multiprecision", "math", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.mpfr.org/"
    license = "LGPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "exact_int": ["mpir", "gmp",]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "exact_int": "gmp",
    }

    exports_sources = "CMakeLists.txt.in", "patches/**"
    generators = "cmake"

    _autotools = None
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.exact_int == "gmp":
            self.requires("gmp/6.2.1")
        elif self.options.exact_int == "mpir":
            self.requires("mpir/3.0.0")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-thread-safe",
            "--with-gmp-include={}".format(tools.unix_path(os.path.join(self.deps_cpp_info[str(self.options.exact_int)].rootpath, "include"))),
            "--with-gmp-lib={}".format(tools.unix_path(os.path.join(self.deps_cpp_info[str(self.options.exact_int)].rootpath, "lib"))),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        if self.settings.compiler == "clang":
            # warning: optimization flag '-ffloat-store' is not supported
            args.append("mpfr_cv_gcc_floatconv_bug=no")
            if self.settings.arch == "x86":
                # fatal error: error in backend: Unsupported library call operation!
                args.append("--disable-float128")
        if self.options.exact_int == "mpir":
            self._autotools.include_paths.append(self.build_folder)
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
        self._autotools.libs = []
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(source_dir=os.path.join(self._source_subfolder, "src"))
        return self._cmake

    def _extract_makefile_variable(self, makefile, variable):
        makefile_contents = tools.load(makefile)
        match = re.search("{}[ \t]*=[ \t]*((?:(?:[a-zA-Z0-9 \t.=/_-])|(?:\\\\\"))*(?:\\\\\n(?:(?:[a-zA-Z0-9 \t.=/_-])|(?:\\\"))*)*)\n".format(variable), makefile_contents)
        if not match:
            raise ConanException("Cannot extract variable {} from {}".format(variable, makefile_contents))
        lines = [line.strip(" \t\\") for line in match.group(1).split()]
        return [item for line in lines for item in shlex.split(line) if item]

    def _extract_mpfr_autotools_variables(self):
        makefile_am = os.path.join(self._source_subfolder, "src", "Makefile.am")
        makefile = os.path.join("src", "Makefile")
        sources = self._extract_makefile_variable(makefile_am, "libmpfr_la_SOURCES")
        headers = self._extract_makefile_variable(makefile_am, "include_HEADERS")
        defs = self._extract_makefile_variable(makefile, "DEFS")
        return sources, headers, defs

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "AR": "lib",
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                    "LD": "link",
                    "NM": "dumpbin -symbols",
                    "OBJDUMP": ":",
                    "RANLIB": ":",
                    "STRIP": ":",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.options.exact_int == "mpir":
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                                       "-lgmp", "-lmpir")
            tools.replace_in_file(os.path.join(self._source_subfolder, "src", "mpfr.h"),
                                       "<gmp.h>", "<mpir.h>")
            tools.save("gmp.h", "#pragma once\n#include <mpir.h>\n")
        with self._build_context():
            autotools = self._configure_autotools()
        if self.settings.os == "Windows":
            cmakelists_in = tools.load("CMakeLists.txt.in")
            sources, headers, definitions = self._extract_mpfr_autotools_variables()
            tools.save(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"), cmakelists_in.format(
                mpfr_sources=" ".join(sources),
                mpfr_headers=" ".join(headers),
                definitions=" ".join(definitions),
            ))
            cmake = self._configure_cmake()
            cmake.build()
        else:
            autotools.make(args=["V=0"])

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.install()
        else:
            autotools = self._configure_autotools()
            autotools.install()
            os.unlink(os.path.join(self.package_folder, "lib", "libmpfr.la"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["mpfr"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines = ["MPFR_DLL"]
