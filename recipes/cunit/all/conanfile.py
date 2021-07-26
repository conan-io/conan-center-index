from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import glob
import os


class CunitConan(ConanFile):
    name = "cunit"
    description = "A Unit Testing Framework for C"
    topics = ("conan", "cunit", "testing")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://cunit.sourceforge.net/"
    license = "BSD-3-Clause"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_automated": [True, False],
        "enable_basic": [True, False],
        "enable_console": [True, False],
        "with_curses": [False, "ncurses"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_automated": True,
        "enable_basic": True,
        "enable_console": True,
        "with_curses": False,
    }
    exports_sources = "patches/**"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_curses == "ncurses":
            self.requires("ncurses/6.2")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")
        self.build_requires("libtool/2.4.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("CUnit-{}".format(self.version), self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            for f in glob.glob("*.c"):
                os.chmod(f, 0o644)

    @contextmanager
    def _build_context(self):
        env = {}
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env.update({
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                    "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "NM": "dumpbin -symbols",
                    "OBJDUMP": ":",
                    "RANLIB": ":",
                    "STRIP": ":",
                })
                with tools.environment_append(env):
                    yield
        else:
            with tools.environment_append(env):
                yield

    def _configure_autools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
        conf_args = [
            "--datarootdir={}".format(os.path.join(self.package_folder, "bin", "share").replace("\\", "/")),
            "--enable-debug" if self.settings.build_type == "Debug" else "--disable-debug",
            "--enable-automated" if self.options.enable_automated else "--disable-automated",
            "--enable-basic" if self.options.enable_basic else "--disable-basic",
            "--enable-console" if self.options.enable_console else "--disable-console",
            "--enable-curses" if self.options.with_curses != False else "--disable-curses",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with self._build_context():
            with tools.chdir(self._source_subfolder):
                self.run("autoreconf -fiv".format(os.environ["AUTORECONF"]), win_bash=tools.os_info.is_windows)
                autotools = self._configure_autools()
                autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autools()
                autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libcunit.la"))
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "man"))
        tools.rmdir(os.path.join(self.package_folder, "doc"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CUnit"
        self.cpp_info.names["cmake_find_package_multi"] = "CUnit"
        libname = "cunit"
        if self.settings.os == "Windows" and self.options.shared:
            libname += ".dll" + (".lib" if self.settings.compiler == "Visual Studio" else ".a")
        self.cpp_info.libs = [libname]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("CU_DLL")
