from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os

required_conan_version = ">=1.33.0"


class CddlibConan(ConanFile):
    name = "cddlib"
    description = (
        "The C-library cddlib is a C implementation of the Double Description "
        "Method of Motzkin et al. for generating all vertices (i.e. extreme points) "
        "and extreme rays of a general convex polyhedron in R^d given by a "
        "system of linear inequalities."
    )
    license = "GPL-2.0-only"
    topics = ("cddlib", "linear-programming", "mathematics", "polyhedra")
    homepage = "https://github.com/cddlib/cddlib"
    url = "https://github.com/conan-io/conan-center-index"

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("gmp/6.2.1")

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("cddlib does not support shared with Visual Studio")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "CC": "{} cl -nologo".format(tools.unix_path(self._user_info_build["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self._user_info_build["automake"].compile)),
                    "LD": "{} link -nologo".format(tools.unix_path(self._user_info_build["automake"].compile)),
                    "AR": "{} lib".format(tools.unix_path(self._user_info_build["automake"].ar_lib)),
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
        args = [
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
        ]
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) >= "12":
            self._autotools.flags.append("-FS")
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        if self.settings.os == "Windows" and self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*[!.dll]")
        else:
            tools.rmdir(os.path.join(self.package_folder, "bin"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "cddlib"
        self.cpp_info.libs = ["cdd", "cddgmp"]
