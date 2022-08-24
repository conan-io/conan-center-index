from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import contextlib
import os
import shutil

required_conan_version = ">=1.33.0"


class CoinUtilsConan(ConanFile):
    name = "coin-utils"
    description = "CoinUtils is an open-source collection of classes and helper functions that are generally useful to multiple COIN-OR projects."
    topics = ("coin-utils", "sparse", "matrix", "helper", "parsing", "representation")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or/CoinUtils"
    license = ("EPL-2.0",)
    settings = "os", "arch", "build_type", "compiler"
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

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.11")
        self.requires("bzip2/1.0.8")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("coin-utils does not provide a shared library on Windows")
        # FIXME: This issue likely comes from very old autotools versions used to produce configure.
        #        It might be fixed by calling autoreconf, but https://github.com/coin-or-tools/BuildTools
        #        should be packaged and added to build requirements.
        if hasattr(self, "settings_build") and tools.build.cross_building(self, self) and self.options.shared:
            raise ConanInvalidConfiguration("coin-utils shared not supported yet when cross-building")

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            self.build_requires("gnu-config/cci.20201022")

        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "{} cl -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                    "LD": "link -nologo",
                    "AR": "{} lib".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].ar_lib)),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        if self.settings.compiler == "Visual Studio":
            self._autotools.cxx_flags.append("-EHsc")
            if tools.scm.Version(self.settings.compiler.version) >= "12":
                self._autotools.flags.append("-FS")
        yes_no = lambda v: "yes" if v else "no"
        configure_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        if self.settings.compiler == "Visual Studio":
            configure_args.append("--enable-msvc={}".format(self.settings.compiler.runtime))
        self._autotools.configure(configure_dir=self._source_subfolder, args=configure_args)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        if self.settings.compiler != "Visual Studio":
            shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                        os.path.join(self._source_subfolder, "config.sub"))
            shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                        os.path.join(self._source_subfolder, "config.guess"))
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install(args=["-j1"])

        tools.files.rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

        if self.settings.compiler == "Visual Studio":
            os.rename(os.path.join(self.package_folder, "lib", "libCoinUtils.a"),
                      os.path.join(self.package_folder, "lib", "CoinUtils.lib"))

    def package_info(self):
        self.cpp_info.libs = ["CoinUtils"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["m"]
        self.cpp_info.includedirs.append(os.path.join("include", "coin"))
        self.cpp_info.names["pkg_config"] = "coinutils"
