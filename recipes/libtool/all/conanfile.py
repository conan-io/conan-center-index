from contextlib import contextmanager
import os
import re
from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanException


class LibtoolConan(ConanFile):
    name = "libtool"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/libtool/"
    description = "GNU libtool is a generic library support script. "
    topics = ("conan", "libtool", "configure", "library", "shared", "static")
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    exports_sources = "patches/**"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    _autotools = None

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def requirements(self):
        self.requires("automake/1.16.1")

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ \
                and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    @contextmanager
    def _build_context(self):
        with tools.environment_append(self._libtool_relocatable_env):
            if self.settings.compiler == "Visual Studio":
                with tools.vcvars(self.settings):
                    with tools.environment_append({"CC": "cl -nologo", "CXX": "cl -nologo",}):
                        yield
            else:
                yield

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "bin", "share")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
        conf_args = [
            "--datarootdir={}".format(tools.unix_path(self._datarootdir)),
            "--prefix={}".format(tools.unix_path(self.package_folder)),
            "--enable-shared",
            "--enable-static",
            "--enable-ltdl-install",
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    @property
    def _shared_ext(self):
        if self.settings.os == "Windows":
            return "dll"
        elif tools.is_apple_os(self.settings.os):
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

        tools.rmdir(os.path.join(self._datarootdir, "info"))
        tools.rmdir(os.path.join(self._datarootdir, "man"))

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
            os.rename(os.path.join(binpath, "libtoolize"),
                      os.path.join(binpath, "libtoolize.exe"))
            os.rename(os.path.join(binpath, "libtool"),
                      os.path.join(binpath, "libtool.exe"))

    @property
    def _libtool_relocatable_env(self):
        return {
            "LIBTOOL_PREFIX": tools.unix_path(self.package_folder),
            "LIBTOOL_DATADIR": tools.unix_path(self._datarootdir),
            "LIBTOOL_PKGAUXDIR": tools.unix_path(os.path.join(self._datarootdir, "libtool", "build-aux")),
            "LIBTOOL_PKGLTDLDIR": tools.unix_path(os.path.join(self._datarootdir, "libtool")),
            "LIBTOOL_ACLOCALDIR": tools.unix_path(os.path.join(self._datarootdir, "aclocal")),
        }

    def package_info(self):
        lib = "ltdl"
        if self.settings.os == "Windows" and self.options.shared:
            lib += ".dll" + ".lib" if self.settings.compiler == "Visual Studio" else ".a"
        self.cpp_info.libs = [lib]

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

        libtoolize = tools.unix_path(os.path.join(self.package_folder, "bin", "libtoolize" + bin_ext))
        self.output.info("Setting LIBTOOLIZE env to {}".format(libtoolize))
        self.env_info.LIBTOOLIZE = libtoolize

        libtool_aclocal = tools.unix_path(os.path.join(self.package_folder, "bin", "share", "aclocal" + bin_ext))
        self.output.info("Appending ACLOCAL_PATH env: {}".format(libtool_aclocal))
        self.env_info.ACLOCAL_PATH.append(libtool_aclocal)

        for key, value in self._libtool_relocatable_env.items():
            self.output.info("Setting {} environment variable to {}".format(key, value))
            setattr(self.env_info, key, value)
