from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import glob
import os

required_conan_version = ">=1.33.0"


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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)
        with tools.files.chdir(self, self._source_subfolder):
            for f in glob.glob("*.c"):
                os.chmod(f, 0o644)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    @contextmanager
    def _build_context(self):
        env = {}
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env.update({
                    "AR": "{} lib".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].ar_lib)),
                    "CC": "{} cl -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
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

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        host, build = None, None
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
            # MSVC canonical names aren't understood
            host, build = False, False
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
        self._autotools.configure(args=conf_args, host=host, build=build)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        with self._build_context():
            with tools.files.chdir(self, self._source_subfolder):
                self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            with tools.files.chdir(self, self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.install()

        if self.settings.compiler == "Visual Studio" and self.options.shared:
            tools.files.rename(self, os.path.join(self.package_folder, "lib", "cunit.dll.lib"),
                         os.path.join(self.package_folder, "lib", "cunit.lib"))

        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
        tools.files.rmdir(self, os.path.join(self.package_folder, "bin", "share", "man"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "doc"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CUnit"
        self.cpp_info.names["cmake_find_package_multi"] = "CUnit"
        self.cpp_info.libs = ["cunit"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("CU_DLL")
