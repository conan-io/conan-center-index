import os
import re
import shlex

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import (
    apply_conandata_patches, copy, export_conandata_patches, get, load,
    replace_in_file, rm, rmdir, save
)
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, check_min_vs, unix_path

required_conan_version = ">=1.58.0"


class MpfrConan(ConanFile):
    name = "mpfr"
    description = "The MPFR library is a C library for multiple-precision floating-point computations with " \
                  "correct rounding"
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.mpfr.org/"
    topics = ("multiprecision", "math", "mathematics")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "exact_int": ["mpir", "gmp"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "exact_int": "gmp",
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        copy(self, "CMakeLists.txt.in", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        if self.settings.os == "Windows":
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.exact_int == "gmp":
            self.requires("gmp/6.3.0", transitive_headers=True)
        elif self.options.exact_int == "mpir":
            self.requires("mpir/3.0.0")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        if self.settings.os == "Windows":
            if is_msvc(self) and not check_min_vs(self, 193, raise_invalid=False) and \
                not self.conf.get("tools.cmake.cmaketoolchain:generator", check_type=str):
                # Use NMake to workaround bug in MSBuild versions prior to 2022 that shows up as:
                #    error MSB6001: Invalid command line switch for "cmd.exe". System.ArgumentException: Item
                #                   has already been added. Key in dictionary: 'tmp'  Key being added: 'TMP'
                self.conf.define("tools.cmake.cmaketoolchain:generator", "NMake Makefiles")
            tc = CMakeToolchain(self)
            tc.generate()
            tc = CMakeDeps(self)
            tc.generate()
        else: # Even with multiple toolchains (see below), can only have one "deps" generator as multiple ones will collide
            tc = AutotoolsDeps(self)
            tc.generate()

        # Setup autotools on all platforms because we need to run autotools.configure when using CMake
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--enable-thread-safe")
        tc.configure_args.append(f'--with-gmp={unix_path(self, self.dependencies[str(self.options.exact_int)].package_folder)}')
        if self.settings.compiler == "clang":
            # warning: optimization flag '-ffloat-store' is not supported
            tc.configure_args.append("mpfr_cv_gcc_floatconv_bug=no")
            if self.settings.arch == "x86":
                # fatal error: error in backend: Unsupported library call operation!
                tc.configure_args.append("--disable-float128")

        if self.options.exact_int == "mpir":
            tc.extra_cflags.append(f"-I{self.build_folder}")
        if is_msvc(self) and check_min_vs(self, "180", raise_invalid=False):
            tc.extra_cflags.append("-FS")

        env = tc.environment()
        if is_msvc(self):
            env.define("CC", "cl -nologo")
            env.define("CXX", "cl -nologo")
        tc.generate(env) # Create conanbuild.conf

    def _extract_makefile_variable(self, makefile, variable):
        makefile_contents = load(self, makefile)
        match = re.search(f'{variable}[ \t]*=[ \t]*((?:(?:[a-zA-Z0-9 \t.=/_-])|(?:\\\\\"))*(?:\\\\\n(?:(?:[a-zA-Z0-9 \t.=/_-])|(?:\\\"))*)*)\n', makefile_contents)
        if not match:
            raise ConanException(f"Cannot extract variable {variable} from {makefile_contents}")
        lines = [line.strip(" \t\\") for line in match.group(1).split()]
        return [item for line in lines for item in shlex.split(line) if item]

    def _extract_mpfr_autotools_variables(self):
        makefile_am = os.path.join(self.source_folder, "src", "Makefile.am") # src/src/Makefile.am
        makefile = os.path.join("src", "Makefile")
        sources = self._extract_makefile_variable(makefile_am, "libmpfr_la_SOURCES")
        headers = self._extract_makefile_variable(makefile_am, "include_HEADERS")
        defs = self._extract_makefile_variable(makefile, "DEFS")
        return sources, headers, defs

    def _patch_sources(self):
        apply_conandata_patches(self)
        if self.settings.os == "Windows": # Allow mixed shared and static libs
            replace_in_file(self, os.path.join(self.source_folder, "configure"),
                'as_fn_error $? "libgmp isn\'t provided as a DLL: use --enable-static --disable-shared" "$LINENO" 5',
                '# as_fn_error $? "libgmp isn\'t provided as a DLL: use --enable-static --disable-shared" "$LINENO" 5')
            replace_in_file(self, os.path.join(self.source_folder, "configure"),
                'as_fn_error $? "libgmp is provided as a DLL: use --disable-static --enable-shared" "$LINENO" 5',
                '# as_fn_error $? "libgmp is provided as a DLL: use --disable-static --enable-shared" "$LINENO" 5')

        if self.options.exact_int == "mpir":
            replace_in_file(self, os.path.join(self.source_folder, "configure"),
                                       "-lgmp", "-lmpir")
            replace_in_file(self, os.path.join(self.source_folder, "src", "mpfr.h"),
                                       "<gmp.h>", "<mpir.h>")
            save(self, "gmp.h", "#pragma once\n#include <mpir.h>\n")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure() # Need to generate Makefile to extract variables for CMake below

        if self.settings.os == "Windows":
            cmakelists_in = load(self, os.path.join(self.export_sources_folder, "CMakeLists.txt.in"))
            sources, headers, definitions = self._extract_mpfr_autotools_variables()
            sources = ["src/" + src for src in sources]
            headers = ["src/" + hdr for hdr in headers]
            save(self, os.path.join(self.source_folder, "CMakeLists.txt"), cmakelists_in.format(
                mpfr_sources=" ".join(sources),
                mpfr_headers=" ".join(headers),
                definitions=" ".join(definitions),
            ))
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            autotools.make(args=["V=0"])

    def package(self):
        copy(self, "COPYING.LESSER", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.install()
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "share"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "mpfr")
        self.cpp_info.libs = ["mpfr"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines = ["MPFR_DLL"]
