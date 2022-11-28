from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import cross_building
from conan.tools.apple import is_apple_os
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv, Environment
from conan.tools.layout import basic_layout
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.files import (
copy,
rmdir,
replace_in_file,
rename,
get,
apply_conandata_patches,
export_conandata_patches
)
from conan.tools.microsoft import is_msvc, unix_path

import os
import re
import shutil

required_conan_version = ">=1.53.0"


class LibtoolConan(ConanFile):
    name = "libtool"
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
    #short_paths = True

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

    def requirements(self):
        self.requires("automake/1.16.5")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")
        self.tool_requires("gnu-config/cci.20210814")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args += [
            "--enable-ltdl-install",
            "--datarootdir=/res"
        ]
        tc.generate()

        env = Environment()
        for key, value in self._libtool_relocatable_env.items():
            env.define_path(key, value)
        if is_msvc(self):
            compile_wrapper = unix_path(self, self._user_info_build["automake"].compile)
            ar_wrapper = unix_path(self, self._user_info_build["automake"].ar_lib)
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")

        env.vars(self).save_script("conanbuild_libtool")

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def _patch_sources(self):
        apply_conandata_patches(self)
        build_aux_folder = os.path.join(self.source_folder, "build-aux")
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB, os.path.join(build_aux_folder, "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS, os.path.join(build_aux_folder, "config.guess"))

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
        for dir in (
                os.path.join(self.package_folder, "bin"),
                os.path.join(self.package_folder, "lib"),
        ):
            for file in os.listdir(dir):
                if regex_in.match(file) and not regex_out.match(file):
                    os.unlink(os.path.join(dir, file))

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "res")

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        res_dir = os.path.join(self.package_folder, "res")
        rmdir(self, os.path.join(res_dir, "info"))
        rmdir(self, os.path.join(res_dir, "man"))

        os.unlink(os.path.join(self.package_folder, "lib", "libltdl.la"))
        if self.options.shared:
            self._rm_binlib_files_containing(self._static_ext, self._shared_ext)
        else:
            self._rm_binlib_files_containing(self._shared_ext)

        import re
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

        if is_msvc(self) and self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "ltdl.dll.lib"),
                         os.path.join(self.package_folder, "lib", "ltdl.lib"))

        # allow libtool to link static libs into shared for more platforms
        libtool_m4 = os.path.join(self._datarootdir, "aclocal", "libtool.m4")
        method_pass_all = "lt_cv_deplibs_check_method=pass_all"
        replace_in_file(self, libtool_m4,
                              "lt_cv_deplibs_check_method='file_magic ^x86 archive import|^x86 DLL'",
                              method_pass_all)
        replace_in_file(self, libtool_m4,
                              "lt_cv_deplibs_check_method='file_magic file format (pei*-i386(.*architecture: i386)?|pe-arm-wince|pe-x86-64)'",
                              method_pass_all)

    @property
    def _libtool_relocatable_env(self):
        return {
            "LIBTOOL_PREFIX": unix_path(self, self.package_folder),
            "LIBTOOL_DATADIR": unix_path(self, self._datarootdir),
            "LIBTOOL_PKGAUXDIR": unix_path(self, os.path.join(self._datarootdir, "libtool", "build-aux")),
            "LIBTOOL_PKGLTDLDIR": unix_path(self, os.path.join(self._datarootdir, "libtool")),
            "LIBTOOL_ACLOCALDIR": unix_path(self, os.path.join(self._datarootdir, "aclocal")),
        }

    def package_info(self):
        self.cpp_info.libs = ["ltdl"]

        if self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.defines = ["LIBLTDL_DLL_IMPORT"]
        else:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["dl"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.buildenv_info.append_path("PATH", bin_path)

        bin_ext = ".exe" if self.settings.os == "Windows" else ""

        libtoolize = unix_path(self, os.path.join(self.package_folder, "bin", "libtoolize" + bin_ext))
        self.output.info("Setting LIBTOOLIZE env to {}".format(libtoolize))
        self.env_info.LIBTOOLIZE = libtoolize
        self.buildenv_info.define("LIBTOOLIZE", libtoolize)

        for key, value in self._libtool_relocatable_env.items():
            self.output.info("Setting {} environment variable to {}".format(key, value))
            setattr(self.env_info, key, value)
            self.buildenv_info.define(key, value)

        libtool_aclocal = unix_path(self, os.path.join(self._datarootdir, "aclocal"))

        self.output.info("Appending ACLOCAL_PATH env: {}".format(libtool_aclocal))
        self.env_info.ACLOCAL_PATH.append(libtool_aclocal)
        self.buildenv_info.append_path("ACLOCAL_PATH", libtool_aclocal)

        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment variable: {}".format(libtool_aclocal))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(libtool_aclocal)
        self.buildenv_info.append_path("AUTOMAKE_CONAN_INCUDES", libtool_aclocal)
