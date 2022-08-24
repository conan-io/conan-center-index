from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os
import shutil

required_conan_version = ">=1.33.0"

class CoinCbcConan(ConanFile):
    name = "coin-cbc"
    description = "COIN-OR Branch-and-Cut solver"
    topics = ("clp", "simplex", "solver", "linear", "programming")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or/Clp"
    license = ("EPL-2.0",)
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "parallel": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "parallel": False,
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
        self.requires("coin-cgl/0.60.3")
        if self.settings.compiler == "Visual Studio" and self.options.parallel:
            self.requires("pthreads4w/3.0.0")    

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def build_requirements(self):
        self.build_requires("gnu-config/cci.20201022")
        self.build_requires("pkgconf/1.7.4")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.4")
    
    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("coin-cbc does not support shared builds on Windows")
        # FIXME: This issue likely comes from very old autotools versions used to produce configure.
        if hasattr(self, "settings_build") and tools.cross_building(self) and self.options.shared:
            raise ConanInvalidConfiguration("coin-cbc shared not supported yet when cross-building")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
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
            "--enable-cbc-parallel={}".format(yes_no(self.options.parallel)),
            "--without-blas",
            "--without-lapack",
        ]
        if self.settings.compiler == "Visual Studio":
            self._autotools.cxx_flags.append("-EHsc")
            configure_args.append("--enable-msvc={}".format(self.settings.compiler.runtime))
            if tools.Version(self.settings.compiler.version) >= 12:
                self._autotools.flags.append("-FS")
            if self.options.parallel:
                configure_args.append("--with-pthreadsw32-lib={}".format(tools.unix_path(os.path.join(self.deps_cpp_info["pthreads4w"].lib_paths[0], self.deps_cpp_info["pthreads4w"].libs[0] + ".lib"))))
                configure_args.append("--with-pthreadsw32-incdir={}".format(tools.unix_path(self.deps_cpp_info["pthreads4w"].include_paths[0])))
        self._autotools.configure(configure_dir=os.path.join(self.source_folder, self._source_subfolder), args=configure_args)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config.guess"))
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        # Installation script expects include/coin to already exist
        tools.files.mkdir(self, os.path.join(self.package_folder, "include", "coin"))
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        for l in ("CbcSolver", "Cbc", "OsiCbc"):
            os.unlink(os.path.join(self.package_folder, "lib", "lib{}.la").format(l))
            if self.settings.compiler == "Visual Studio":
                os.rename(os.path.join(self.package_folder, "lib", "lib{}.a").format(l),
                          os.path.join(self.package_folder, "lib", "{}.lib").format(l))

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["libcbc"].libs = ["CbcSolver", "Cbc"]
        self.cpp_info.components["libcbc"].includedirs.append(os.path.join("include", "coin"))
        self.cpp_info.components["libcbc"].requires = ["coin-clp::osi-clp", "coin-utils::coin-utils", "coin-osi::coin-osi", "coin-cgl::coin-cgl"]
        self.cpp_info.components["libcbc"].names["pkg_config"] = "cbc"
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.parallel:
            self.cpp_info.components["libcbc"].system_libs.append("pthread")
        if self.settings.os in ["Windows"] and self.options.parallel:
            self.cpp_info.components["libcbc"].requires.append("pthreads4w::pthreads4w")

        self.cpp_info.components["osi-cbc"].libs = ["OsiCbc"]
        self.cpp_info.components["osi-cbc"].requires = ["libcbc"]
        self.cpp_info.components["osi-cbc"].names["pkg_config"] = "osi-cbc"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
