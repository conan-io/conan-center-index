from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, mkdir, rmdir, rename, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path, unix_path_package_info_legacy
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.errors import ConanException
import os
import re
import shutil

required_conan_version = ">=1.57.0"

class LibtoolConan(ConanFile):
    name = "libtool"
    # package_type = "application", "library" # Hybrid package_type not yet supported
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/libtool/"
    description = "GNU libtool is a generic library support script. "
    topics = ("conan", "libtool", "configure", "library", "shared", "static")
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.tool_requires("m4/1.4.19")               # Needed by configure
        self.tool_requires("gnu-config/cci.20210814") # Needed for config.sub and config.guess
        if self._settings_build.os == "Windows":
            self.win_bash = True
            self.tool_requires("automake/1.16.5")     # Needed for complie and lib wrappers
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        if (self.settings.get_safe("compiler") == "Visual Studio" and self.settings.get_safe("compiler.version") >= "12") or \
           (self.settings.get_safe("compiler") == "msvc" and self.settings.get_safe("compiler.version") >= "180"):
            tc.extra_cflags.append("-FS")
        tc.configure_args.append("--enable-shared")
        tc.configure_args.append("--enable-static")
        tc.configure_args.append("--enable-ltdl-install")
        env = tc.environment()
        if is_msvc(self):
            env.append("CC", f'{unix_path(self, self.conf.get("user.automake:compile-wrapper"))} cl -nologo')
            env.append("CXX", f'{unix_path(self, self.conf.get("user.automake:compile-wrapper"))} cl -nologo')
            env.append("AR", f'{unix_path(self, self.conf.get("user.automake:lib-wrapper"))} lib')
            env.append("LD", "link")
            env.define("F77", "no")
            env.define("FC", "no")
        tc.generate(env)

    def _patch_sources(self):
        apply_conandata_patches(self)
        shutil.copy(self.conf.get("user.gnu-config:config_sub"),
                    os.path.join(self.source_folder, "build-aux", "config.sub"))
        shutil.copy(self.conf.get("user.gnu-config:config_guess"),
                    os.path.join(self.source_folder, "build-aux", "config.guess"))

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
        if is_msvc(self):
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
        copy(self, "COPYING*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        fix_apple_shared_install_name(self)

        rmdir(self, os.path.join(self.package_folder, "share", "info"))
        rmdir(self, os.path.join(self.package_folder, "share", "man"))

        os.unlink(os.path.join(self.package_folder, "lib", "libltdl.la"))
        if self.options.shared:
            if not is_msvc(self): # Don't delete Windows import lib
                self._rm_binlib_files_containing(self._static_ext)
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
            contents = open(file, encoding='UTF-8').read()
            for key, repl in replaces.items():
                contents, nb1 = re.subn(f'^{key}=\"[^\"]*\"', f'{key}=\"{repl}\"', contents, flags=re.MULTILINE)
                contents, nb2 = re.subn(f'^: \\$\\{{{key}=\"[^$\"]*\"\\}}', f': ${{{key}=\"{repl}\"}}', contents, flags=re.MULTILINE)
                if nb1 + nb2 == 0:
                    raise ConanException(f'Failed to find {key} in {repl}')
            open(file, "w", encoding='UTF-8').write(contents)

        binpath = os.path.join(self.package_folder, "bin")
        if self.settings.os == "Windows":
            rename(self, os.path.join(binpath, "libtoolize"),
                         os.path.join(binpath, "libtoolize.exe"))
            rename(self, os.path.join(binpath, "libtool"),
                         os.path.join(binpath, "libtool.exe"))

        if is_msvc(self) and self.options.shared:
            # Remove static (archive) library
            os.unlink(os.path.join(self.package_folder, "lib", "ltdl.lib"))
            # Rename import library
            rename(self, os.path.join(self.package_folder, "lib", "ltdl.dll.lib"),
                         os.path.join(self.package_folder, "lib", "ltdl.lib"))

        # allow libtool to link static libs into shared for more platforms
        libtool_m4 = os.path.join(self.package_folder, "share", "aclocal", "libtool.m4")
        method_pass_all = "lt_cv_deplibs_check_method=pass_all"
        replace_in_file(self, libtool_m4,
                              "lt_cv_deplibs_check_method='file_magic ^x86 archive import|^x86 DLL'",
                              method_pass_all)
        replace_in_file(self, libtool_m4,
                              "lt_cv_deplibs_check_method='file_magic file format (pei*-i386(.*architecture: i386)?|pe-arm-wince|pe-x86-64)'",
                              method_pass_all)

        mkdir(self, os.path.join(self.package_folder, "res"))
        rename(self, os.path.join(self.package_folder, "share", "aclocal"),
                     os.path.join(self.package_folder, "res", "aclocal"))
        rename(self, os.path.join(self.package_folder, "share", "libtool"),
                     os.path.join(self.package_folder, "res", "libtool"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libtool")
        self.cpp_info.libs = ["ltdl"]
        self.cpp_info.resdirs = ["res/aclocal", "res/libtool"]

        if self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.defines = ["LIBLTDL_DLL_IMPORT"]
        else:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["dl"]

        # Use ACLOCAL_PATH to access the .m4 files provided with libtool
        aclocal_path = os.path.join(self.package_folder, "res", "aclocal")
        self.buildenv_info.append_path("ACLOCAL_PATH", aclocal_path)

        # Everything below can be eliminated when Conan 1.x support is dropped
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f'Appending PATH env: {bin_path}')
        self.env_info.PATH.append(bin_path)

        bin_ext = ".exe" if self.settings.os == "Windows" else ""

        libtoolize = os.path.join(self.package_folder, "bin", "libtoolize" + bin_ext)
        libtoolize = "/" + libtoolize.replace("\\", "/").replace(":", "") # Can't use unix_path with Conan 2.0
        self.output.info(f'Setting LIBTOOLIZE env to {libtoolize}')
        self.env_info.LIBTOOLIZE = libtoolize

        aclocal_path = unix_path_package_info_legacy(self, aclocal_path)
        self.output.info(f'Appending ACLOCAL_PATH env: {aclocal_path}')
        self.env_info.ACLOCAL_PATH.append(aclocal_path)
        self.output.info(f'Appending AUTOMAKE_CONAN_INCLUDES environment variable: {aclocal_path}')
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(aclocal_path)
