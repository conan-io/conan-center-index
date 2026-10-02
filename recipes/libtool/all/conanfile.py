from conan import ConanFile
from conan.errors import ConanException
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.env import Environment
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rename, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

import os
import re
import shutil

required_conan_version = ">=2.4"


class LibtoolConan(ConanFile):
    name = "libtool"
    # most common use is as "application", but library traits
    # are a superset of application so this should cover all cases
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/libtool/"
    description = "GNU libtool is a generic library support script. "
    topics = ("configure", "library", "shared", "static")
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    settings = "os", "arch", "compiler", "build_type"
    languages = ["C"]
    implements = ["auto_shared_fpic"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _is_clang_cl(self):
        return self.settings.os == "Windows" and self.settings.compiler == "clang" and \
               self.settings.compiler.get_safe("runtime")

    @property
    def _is_msvc_like(self):
        return is_msvc(self) or self._is_clang_cl

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("automake/1.16.5")

    def build_requirements(self):
        self.tool_requires("automake/1.16.5")
        self.tool_requires("m4/1.4.19")               # Needed by configure
        self.tool_requires("gnu-config/cci.20210814")
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "res")

    def generate(self):
        if is_msvc(self):
            # __VSCMD_ARG_NO_LOGO: this test_package has too many invocations,
            #                      this avoids printing the logo everywhere
            # VSCMD_SKIP_SENDTELEMETRY: avoid the telemetry process holding onto the directory
            #                           unnecessarily
            env = Environment()
            env.define("__VSCMD_ARG_NO_LOGO", "1")
            env.define("VSCMD_SKIP_SENDTELEMETRY", "1")
            env.vars(self, scope="build").save_script("conanbuild_vcvars_options.bat")

        tc = AutotoolsToolchain(self)
        # clang-cl: libtool can't create shared DLLs (LNK1561: entry point must be defined).
        # Disable shared when building static-only to avoid the failing DLL link step.
        enable_shared = "--enable-shared" if not self._is_clang_cl or self.options.shared else "--disable-shared"
        tc.configure_args.extend([
            "--datarootdir=${prefix}/res",
            enable_shared,
            "--enable-static",
            "--enable-ltdl-install",
        ])

        # ltdl.c calls access() without including <io.h>.
        # Clang C99+ treats implicit function declarations as errors.
        # Downgrade to warning — access() links fine via MSVC CRT (_access).
        # Must be set BEFORE tc.environment() — generate(env) uses env's snapshot.
        if self._is_clang_cl:
            tc.extra_cflags += ["-Wno-implicit-function-declaration"]

        env = tc.environment()
        if self._is_msvc_like:
            if self._is_clang_cl:
                env.define("CC", os.environ.get("CC", "clang-cl"))
                env.define("CXX", os.environ.get("CXX", "clang-cl"))
            else:
                env.define("CC", "cl -nologo")
                env.define("CXX", "cl -nologo")

            # Disable Fortran detection to handle issue with VS 2022
            # See: https://savannah.gnu.org/patch/?9313#comment1
            # In the future this could be removed if a new version fixes this
            # upstream
            env.define("F77", "no")
            env.define("FC", "no")
        tc.generate(env)

    def _patch_sources(self):
        apply_conandata_patches(self)
        config_guess =  self.dependencies.build["gnu-config"].conf_info.get("user.gnu-config:config_guess")
        config_sub = self.dependencies.build["gnu-config"].conf_info.get("user.gnu-config:config_sub")
        shutil.copy(config_sub, os.path.join(self.source_folder, "build-aux", "config.sub"))
        shutil.copy(config_guess, os.path.join(self.source_folder, "build-aux", "config.guess"))

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    @property
    def _shared_ext(self):
        if self.settings.os == "Windows":
            return "dll"
        elif is_apple_os(self):
            return "dylib"
        else:
            return "so"

    @property
    def _static_ext(self):
        if self._is_msvc_like:
            return "lib"
        else:
            return "a"

    def _rm_binlib_files_containing(self, ext_inclusive, ext_exclusive=None):
        regex_in = re.compile(r".*\.({})($|\..*)".format(ext_inclusive))
        if ext_exclusive:
            regex_out = re.compile(r".*\.({})($|\..*)".format(ext_exclusive))
        else:
            regex_out = re.compile("^$")
        for directory in (
                os.path.join(self.package_folder, "bin"),
                os.path.join(self.package_folder, "lib"),
        ):
            for file in os.listdir(directory):
                if regex_in.match(file) and not regex_out.match(file):
                    os.unlink(os.path.join(directory, file))

    def package(self):
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        fix_apple_shared_install_name(self)

        rmdir(self, os.path.join(self._datarootdir, "info"))
        rmdir(self, os.path.join(self._datarootdir, "man"))

        os.unlink(os.path.join(self.package_folder, "lib", "libltdl.la"))
        if self.options.shared:
            self._rm_binlib_files_containing(self._static_ext, self._shared_ext)
        else:
            self._rm_binlib_files_containing(self._shared_ext)

        files = (
            os.path.join(self.package_folder, "bin", "libtool"),
            os.path.join(self.package_folder, "bin", "libtoolize"),
        )
        replaces = {
            "GREP": "/usr/bin/env grep",
            "EGREP": "/usr/bin/env grep -E",
            "FGREP": "/usr/bin/env grep -F",
            "SED": "/usr/bin/env sed",
        }
        for file in files:
            contents = open(file).read()
            for key, repl in replaces.items():
                contents, nb1 = re.subn("^{}=\"[^\"]*\"".format(key), "{}=\"{}\"".format(key, repl), contents, flags=re.MULTILINE)
                contents, nb2 = re.subn("^: \\$\\{{{}=\"[^$\"]*\"\\}}".format(key), ": ${{{}=\"{}\"}}".format(key, repl), contents, flags=re.MULTILINE)
                if nb1 + nb2 == 0:
                    raise ConanException("Failed to find {} in {}".format(key, repl))
            open(file, "w").write(contents)

        binpath = os.path.join(self.package_folder, "bin")
        if self.settings.os == "Windows":
            rename(self, os.path.join(binpath, "libtoolize"),
                         os.path.join(binpath, "libtoolize.exe"))
            rename(self, os.path.join(binpath, "libtool"),
                         os.path.join(binpath, "libtool.exe"))

        if self._is_msvc_like and self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "ltdl.dll.lib"),
                         os.path.join(self.package_folder, "lib", "ltdl.lib"))

        # allow libtool to link static libs into shared for more platforms
        libtool_m4 = os.path.join(self._datarootdir, "aclocal", "libtool.m4")
        method_pass_all = "lt_cv_deplibs_check_method=pass_all"
        replace_in_file(self, libtool_m4,
                              "lt_cv_deplibs_check_method='file_magic ^x86 archive import|^x86 DLL'",
                              method_pass_all)
        # 2.5.4 added |pe-aarch64 to the file format pattern
        if Version(self.version) >= "2.5":
            replace_in_file(self, libtool_m4,
                                  "lt_cv_deplibs_check_method='file_magic file format (pei*-i386(.*architecture: i386)?|pe-arm-wince|pe-x86-64|pe-aarch64)'",
                                  method_pass_all)
        else:
            replace_in_file(self, libtool_m4,
                                  "lt_cv_deplibs_check_method='file_magic file format (pei*-i386(.*architecture: i386)?|pe-arm-wince|pe-x86-64)'",
                                  method_pass_all)

    def package_info(self):
        self.cpp_info.libs = ["ltdl"]

        if self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.defines = ["LIBLTDL_DLL_IMPORT"]
        else:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["dl"]

        # Define environment variables such that libtool m4 files are seen by Automake
        libtool_aclocal_dir = os.path.join(self._datarootdir, "aclocal")

        self.buildenv_info.append_path("ACLOCAL_PATH", libtool_aclocal_dir)
        self.buildenv_info.append_path("AUTOMAKE_CONAN_INCLUDES", libtool_aclocal_dir)
        self.runenv_info.append_path("ACLOCAL_PATH", libtool_aclocal_dir)
        self.runenv_info.append_path("AUTOMAKE_CONAN_INCLUDES", libtool_aclocal_dir)
