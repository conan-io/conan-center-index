from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import rename, get, apply_conandata_patches, rmdir
from conan.tools.build import cross_building
from conan.tools.scm import Version
from conans import AutoToolsBuildEnvironment, tools
from contextlib import contextmanager
import os
import shutil

required_conan_version = ">=1.47.0"

class CoinCglConan(ConanFile):
    name = "coin-cgl"
    description = "COIN-OR Cut Generator Library"
    topics = ("cgl", "simplex", "solver", "linear", "programming")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or/Cgl"
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
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("coin-utils/2.11.4")
        self.requires("coin-osi/0.108.6")
        self.requires("coin-clp/1.17.6")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def build_requirements(self):
        self.tool_requires("gnu-config/cci.20201022")
        self.tool_requires("pkgconf/1.7.4")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.tool_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.tool_requires("automake/1.16.5")
            
    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("coin-cgl does not support shared builds on Windows")
        # FIXME: This issue likely comes from very old autotools versions used to produce configure.
        if hasattr(self, "settings_build") and cross_building(self) and self.options.shared:
            raise ConanInvalidConfiguration("coin-cgl shared not supported yet when cross-building")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

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
        configure_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--without-blas",
            "--without-lapack",
        ]
        if self.settings.compiler == "Visual Studio":
            self._autotools.cxx_flags.append("-EHsc")
            configure_args.append(f"--enable-msvc={self.settings.compiler.runtime}")
            if Version(self.settings.compiler.version) >= 12:
                self._autotools.flags.append("-FS")
        self._autotools.configure(configure_dir=os.path.join(self.source_folder, self._source_subfolder), args=configure_args)
        return self._autotools

    def build(self):
        apply_conandata_patches(self)
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
            autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libCgl.la"))

        if self.settings.compiler == "Visual Studio":
            rename(self,
                   os.path.join(self.package_folder, "lib", "libCgl.a"),
                   os.path.join(self.package_folder, "lib", "Cgl.lib"))

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["Cgl"]
        self.cpp_info.includedirs.append(os.path.join("include", "coin"))
        self.cpp_info.names["pkg_config"] = "cgl"
