from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import contextlib
import os

required_conan_version = ">=1.33.0"


class GfCompleteConan(ConanFile):
    name = "gf-complete"
    description = "A library for Galois Field arithmetic"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ceph/gf-complete"
    license = "BSD-3-Clause"
    topics = ("galois field", "math", "algorithms")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "neon": [True, False, "auto"],
        "sse": [True, False, "auto"],
        "avx": [True, False, "auto"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "neon": "auto",
        "sse": "auto",
        "avx": "auto"
    }

    exports_sources = "patches/**"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.sse
            del self.options.avx
        if "arm" not in self.settings.arch:
            del self.options.neon

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.settings.compiler == "Visual Studio":
            self.requires("getopt-for-visual-studio/20200201")

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                raise ConanInvalidConfiguration("gf-complete doesn't support shared with Visual Studio")
            if self.version == "1.03":
                raise ConanInvalidConfiguration("gf-complete 1.03 doesn't support Visual Studio")

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # Don't build tests and examples (and also tools if Visual Studio)
        to_build = ["src"]
        if self.settings.compiler != "Visual Studio":
            to_build.append("tools")
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "Makefile.am"),
                              "SUBDIRS = src tools test examples",
                              "SUBDIRS = {}".format(" ".join(to_build)))
        # Honor build type settings and fPIC option
        for subdir in ["src", "tools"]:
            for flag in ["-O3", "-fPIC"]:
                tools.files.replace_in_file(self, os.path.join(self._source_subfolder, subdir, "Makefile.am"),
                                      flag, "")

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "{} cl -nologo".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].compile)),
                    "LD": "{} link -nologo".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].compile)),
                    "AR": "{} lib".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].ar_lib)),
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
            self._autotools.flags.append("-FS")
        elif "x86" in self.settings.arch:
            self._autotools.flags.append("-mstackrealign")

        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]

        if "arm" in self.settings.arch:
            if self.options.neon != "auto":
                conf_args.append("--enable-neon={}".format(yes_no(self.options.neon)))

        if self.settings.arch in ["x86", "x86_64"]:
            if self.options.sse != "auto":
                conf_args.append("--enable-sse={}".format(yes_no(self.options.sse)))

            if self.options.avx != "auto":
                conf_args.append("--enable-avx={}".format(yes_no(self.options.avx)))

        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)

        return self._autotools

    def build(self):
        self._patch_sources()
        with tools.files.chdir(self, self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        tools.files.rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["gf_complete"]

        if self.settings.compiler != "Visual Studio":
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
