from conans import ConanFile, tools, AutoToolsBuildEnvironment
import contextlib
import os

required_conan_version = ">=1.33.0"


class ImakeConan(ConanFile):
    name = "imake"
    description = "Obsolete C preprocessor interface to the make utility"
    topics = ("conan", "imake", "xmkmf", "preprocessor", "build", "system")
    license = "MIT"
    homepage = "https://gitlab.freedesktop.org/xorg/util/imake"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "ccmakedep": [True, False],
        "cleanlinks": [True, False],
        "makeg": [True, False],
        "mergelib": [True, False],
        "mkdirhier": [True, False],
        "mkhtmlindex": [True, False],
        "revpath": [True, False],
        "xmkmf": [True, False],
    }
    default_options = {
        "ccmakedep": True,
        "cleanlinks": True,
        "makeg": True,
        "mergelib": True,
        "mkdirhier": True,
        "mkhtmlindex": True,
        "revpath": True,
        "xmkmf": True,
    }

    exports_sources = "patches/*"
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires("xorg-proto/2021.4")

    def build_requirements(self):
        self.build_requires("automake/1.16.3")
        self.build_requires("pkgconf/1.7.4")
        if self._settings_build.os == "Windows":
            self.build_requires("msys2/cci.latest")

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "{} cl -nologo".format(tools.unix_path(self._user_info_build["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self._user_info_build["automake"].compile)),
                    "CPP": "{} cl -E".format(tools.unix_path(self._user_info_build["automake"].compile)),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
        self._autotools.libs = []
        if self.settings.os == "Windows":
            self._autotools.defines.append("WIN32")
        if self.settings.compiler == "Visual Studio":
            self._autotools.defines.extend([
                "_CRT_SECURE_NO_WARNINGS",
                "CROSSCOMPILE_CPP",
            ])
            self._autotools.flags.append("-FS")
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-ccmakedep={}".format(yes_no(self.options.ccmakedep)),
            "--enable-cleanlinks={}".format(yes_no(self.options.cleanlinks)),
            "--enable-makeg={}".format(yes_no(self.options.makeg)),
            "--enable-mergelib={}".format(yes_no(self.options.mergelib)),
            "--enable-mkdirhier={}".format(yes_no(self.options.mkdirhier)),
            "--enable-mkhtmlindex={}".format(yes_no(self.options.mkhtmlindex)),
            "--enable-revpath={}".format(yes_no(self.options.revpath)),
            "--enable-xmkmf={}".format(yes_no(self.options.xmkmf)),
        ]

        # FIXME: RAWCPP (ac_cv_path_RAWCPP) is not compatible with MSVC preprocessor. It needs to be cpp.
        if tools.get_env("CPP"):
            conf_args.extend([
                "--with-script-preproc-cmd={}".format(tools.get_env("CPP")),
            ])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # tools.files.replace_in_file(self, os.path.join(self._source_subfolder, ""))
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make(args=["V=1"])

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
