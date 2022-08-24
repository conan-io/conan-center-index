from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanException
from contextlib import contextmanager
import os
import re
import shutil

required_conan_version = ">=1.33.0"


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

    exports_sources = "patches/**"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("automake/1.16.5")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.build_requires("automake/1.16.5")
        self.build_requires("gnu-config/cci.20210814")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextmanager
    def _build_context(self):
        with tools.run_environment(self):
            with tools.environment_append(self._libtool_relocatable_env):
                if self.settings.compiler == "Visual Studio":
                    with tools.vcvars(self.settings):
                        with tools.environment_append({"CC": "cl -nologo", "CXX": "cl -nologo",}):
                            yield
                else:
                    yield

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "res")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.compiler == "Visual Studio" and tools.scm.Version(self, self.settings.compiler.version) >= "12":
            self._autotools.flags.append("-FS")
        conf_args = [
            "--datarootdir={}".format(tools.microsoft.unix_path(self, self._datarootdir)),
            "--prefix={}".format(tools.microsoft.unix_path(self, self.package_folder)),
            "--enable-shared",
            "--enable-static",
            "--enable-ltdl-install",
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.files.patch(self, **patch)
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "build-aux", "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "build-aux", "config.guess"))

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    @property
    def _shared_ext(self):
        if self.settings.os == "Windows":
            return "dll"
        elif tools.is_apple_os(self, self.settings.os):
            return "dylib"
        else:
            return "so"

    @property
    def _static_ext(self):
        if self.settings.compiler == "Visual Studio":
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

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        tools.files.rmdir(self, os.path.join(self._datarootdir, "info"))
        tools.files.rmdir(self, os.path.join(self._datarootdir, "man"))

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
            tools.files.rename(self, os.path.join(binpath, "libtoolize"),
                         os.path.join(binpath, "libtoolize.exe"))
            tools.files.rename(self, os.path.join(binpath, "libtool"),
                         os.path.join(binpath, "libtool.exe"))

        if self.settings.compiler == "Visual Studio" and self.options.shared:
            tools.files.rename(self, os.path.join(self.package_folder, "lib", "ltdl.dll.lib"),
                         os.path.join(self.package_folder, "lib", "ltdl.lib"))

        # allow libtool to link static libs into shared for more platforms
        libtool_m4 = os.path.join(self._datarootdir, "aclocal", "libtool.m4")
        method_pass_all = "lt_cv_deplibs_check_method=pass_all"
        tools.files.replace_in_file(self, libtool_m4,
                              "lt_cv_deplibs_check_method='file_magic ^x86 archive import|^x86 DLL'",
                              method_pass_all)
        tools.files.replace_in_file(self, libtool_m4,
                              "lt_cv_deplibs_check_method='file_magic file format (pei*-i386(.*architecture: i386)?|pe-arm-wince|pe-x86-64)'",
                              method_pass_all)

    @property
    def _libtool_relocatable_env(self):
        return {
            "LIBTOOL_PREFIX": tools.microsoft.unix_path(self, self.package_folder),
            "LIBTOOL_DATADIR": tools.microsoft.unix_path(self, self._datarootdir),
            "LIBTOOL_PKGAUXDIR": tools.microsoft.unix_path(self, os.path.join(self._datarootdir, "libtool", "build-aux")),
            "LIBTOOL_PKGLTDLDIR": tools.microsoft.unix_path(self, os.path.join(self._datarootdir, "libtool")),
            "LIBTOOL_ACLOCALDIR": tools.microsoft.unix_path(self, os.path.join(self._datarootdir, "aclocal")),
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

        bin_ext = ".exe" if self.settings.os == "Windows" else ""

        libtoolize = tools.microsoft.unix_path(self, os.path.join(self.package_folder, "bin", "libtoolize" + bin_ext))
        self.output.info("Setting LIBTOOLIZE env to {}".format(libtoolize))
        self.env_info.LIBTOOLIZE = libtoolize

        for key, value in self._libtool_relocatable_env.items():
            self.output.info("Setting {} environment variable to {}".format(key, value))
            setattr(self.env_info, key, value)

        libtool_aclocal = tools.microsoft.unix_path(self, os.path.join(self._datarootdir, "aclocal"))
        self.output.info("Appending ACLOCAL_PATH env: {}".format(libtool_aclocal))
        self.env_info.ACLOCAL_PATH.append(libtool_aclocal)
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment variable: {}".format(libtool_aclocal))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(libtool_aclocal)
