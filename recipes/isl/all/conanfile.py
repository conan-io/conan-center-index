from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os

required_conan_version = ">=1.33.0"


class IslConan(ConanFile):
    name = "isl"
    description = "isl is a library for manipulating sets and relations of integer points bounded by linear constraints."
    topics = ("isl", "integer", "set", "library")
    license = "MIT"
    homepage = "https://libisl.sourceforge.io"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_int": ["gmp", "imath", "imath-32"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_int": "gmp",
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Cannot build shared isl library on Windows (due to libtool refusing to link to static/import libraries)")
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("Apple M1 is not yet supported. Contributions are welcome")
        if self.options.with_int != "gmp":
            # FIXME: missing imath recipe
            raise ConanInvalidConfiguration("imath is not (yet) available on cci")
        if self.settings.compiler == "Visual Studio" and tools.scm.Version(self, self.settings.compiler.version) < 16 and self.settings.compiler.runtime == "MDd":
            # gmp.lib(bdiv_dbm1c.obj) : fatal error LNK1318: Unexpected PDB error; OK (0)
            raise ConanInvalidConfiguration("isl fails to link with this version of visual studio and MDd runtime")

    def requirements(self):
        if self.options.with_int == "gmp":
            self.requires("gmp/6.2.1")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.4")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "AR": "{} lib".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].ar_lib)),
                    "CC": "{} cl -nologo -{}".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].compile), self.settings.compiler.runtime),
                    "CXX": "{} cl -nologo -{}".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].compile), self.settings.compiler.runtime),
                    "NM": "dumpbin -symbols",
                    "OBJDUMP": ":",
                    "RANLIB": ":",
                    "STRIP": ":",
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
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--with-int={}".format(self.options.with_int),
            "--enable-portable-binary",
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        if self.options.with_int == "gmp":
            conf_args.extend([
                "--with-gmp=system",
                "--with-gmp-prefix={}".format(self.deps_cpp_info["gmp"].rootpath.replace("\\", "/")),
            ])
        if self.settings.compiler == "Visual Studio":
            if tools.scm.Version(self, self.settings.compiler.version) >= 15:
                self._autotools.flags.append("-Zf")
            if tools.scm.Version(self, self.settings.compiler.version) >= 12:
                self._autotools.flags.append("-FS")
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        os.unlink(os.path.join(os.path.join(self.package_folder, "lib", "libisl.la")))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "isl"
        self.cpp_info.libs = ["isl"]
