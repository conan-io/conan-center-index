from conan import ConanFile, tools
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conans.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from contextlib import contextmanager
from conan.tools.files import get, copy, rmdir
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
        if self.settings.compiler == "msvc" and tools.Version(self.settings.compiler.version) < 16 and self.settings.compiler.runtime == "MDd":
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
        if self.settings.compiler == "msvc":
            self.build_requires("automake/1.16.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)
    
    def layout(self):
        self.folders.source = self._source_subfolder
        self.folders.build = self._source_subfolder

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "msvc":
            with tools.vcvars(self.settings):
                env = {
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                    "CC": "{} cl -nologo -{}".format(tools.unix_path(self.deps_user_info["automake"].compile), self.settings.compiler.runtime),
                    "CXX": "{} cl -nologo -{}".format(tools.unix_path(self.deps_user_info["automake"].compile), self.settings.compiler.runtime),
                    "NM": "dumpbin -symbols",
                    "OBJDUMP": ":",
                    "RANLIB": ":",
                    "STRIP": ":",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield
    
    def generate(self):
        if self._autotools:
            return self._autotools
        # TODO: Remove when conan 2.0 is released as this will be default behaviour
        buildenv = VirtualBuildEnv(self)
        buildenv.generate()
        
        self._autotools = AutotoolsToolchain(self)

        # self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        self._autotools.configure_args.extend([
            "--with-int={}".format(self.options.with_int),
            "--enable-portable-binary",
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ])
        if self.options.with_int == "gmp":
            self._autotools.configure_args.extend([
                "--with-gmp=system",
                #"--with-gmp-prefix={}".format(self.deps_cpp_info["gmp"].rootpath.replace("\\", "/")),
                "--with-gmp-prefix={}".format(self.dependencies["gmp"].package_folder.replace("\\", "/")),
            ])
        if self.settings.compiler == "msvc":
            if tools.Version(self.settings.compiler.version) >= 15:
                self._autotools.cflags.append("-Zf")
            if tools.Version(self.settings.compiler.version) >= 12:
                self._autotools.cflags.append("-FS")
        self._autotools.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self._source_subfolder, dst="licenses")
        autotools = Autotools(self)
        autotools.install()

        os.unlink(os.path.join(os.path.join(self.package_folder, "lib", "libisl.la")))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "isl"
        self.cpp_info.libs = ["isl"]
