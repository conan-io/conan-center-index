from conan import ConanFile
from conan.tools.files import save, load, chdir, copy, get, rmdir, replace_in_file, apply_conandata_patches
from conan.tools.layout import basic_layout
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.microsoft import is_msvc, unix_path
from conan.errors import ConanException
import os
import re
import shlex

required_conan_version = ">=1.56.0"


class MpfrConan(ConanFile):
    name = "mpfr"
    package_type = "library"
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


    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        if self.options.exact_int == "gmp":
            self.requires("gmp/6.2.1", transitive_headers=True)
        elif self.options.exact_int == "mpir":
            self.requires("mpir/3.0.0")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def layout(self):
        if self.settings.os == "Windows":
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        if self.settings.os == "Windows":
            tc = CMakeToolchain(self)
            tc.generate()
            tc = CMakeDeps(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.configure_args.append("--enable-thread-safe")
            tc.configure_args.append(f'--with-gmp={unix_path(self, self.dependencies[str(self.options.exact_int)].package_folder)}')
            tc.configure_args.append(f'--enable-shared={"yes" if self.options.shared else "no"}')
            tc.configure_args.append(f'--enable-static={"yes" if not self.options.shared else "no"}')
            if self.settings.compiler == "clang":
                # warning: optimization flag '-ffloat-store' is not supported
                tc.configure_args.append("mpfr_cv_gcc_floatconv_bug=no")
                if self.settings.arch == "x86":
                    # fatal error: error in backend: Unsupported library call operation!
                    tc.configure_args.append("--disable-float128")

            if self.options.exact_int == "mpir":
                tc.extra_cflags.append(f"-I{self.build_folder}")
            if is_msvc(self):
                tc.extra_cflags.append("-FS")

            env = tc.environment()
            if is_msvc(self):
                env.define("AR", "lib")
                env.define("CC", "cl -nologo")
                env.define("CXX", "cl -nologo")
                env.define("LD", "link")
                env.define("NM", "dumpbin -symbols")
                env.define("OBJDUMP", ":")
                env.define("RANLIB", ":")
                env.define("STRIP", ":")
            tc.generate(env) # Create conanbuild.conf
            tc = AutotoolsDeps(self)
            tc.generate()

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

    def build(self):
        with chdir(self, self.source_folder):
            command = "./autogen.sh"
            if os.path.exists(command):
                self.run(command)
        apply_conandata_patches(self)
        if self.options.exact_int == "mpir":
            replace_in_file(self, os.path.join(self.source_folder, "configure"),
                                       "-lgmp", "-lmpir")
            replace_in_file(self, os.path.join(self.source_folder, "src", "mpfr.h"),
                                       "<gmp.h>", "<mpir.h>")
            save(self, "gmp.h", "#pragma once\n#include <mpir.h>\n")

        if self.settings.os == "Windows":
            cmakelists_in = load(self, os.path.join(self.export_sources_folder, "CMakeLists.txt.in"))
            sources, headers, definitions = self._extract_mpfr_autotools_variables()
            save(self, os.path.join(self.source_folder, "CMakeLists.txt"), cmakelists_in.format(
                mpfr_sources=" ".join(sources),
                mpfr_headers=" ".join(headers),
                definitions=" ".join(definitions),
            ))
            cmake = CMake(self)
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make(args=["V=0"])

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.settings.os == "Windows":
            cmake = CMake(self)
            cmake.install()
        else:
            autotools = Autotools(self)
            autotools.install()
            os.unlink(os.path.join(self.package_folder, "lib", "libmpfr.la"))
            rmdir(self, os.path.join(self.package_folder, "share"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "MPFR")
        self.cpp_info.set_property("cmake_target_name", "MPFR::MPFR")
        self.cpp_info.libs = ["mpfr"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines = ["MPFR_DLL"]
