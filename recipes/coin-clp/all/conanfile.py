from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os


class CoinClpConan(ConanFile):
    name = "coin-clp"
    description = "COIN-OR Linear Programming Solver"
    topics = ("conan", "clp", "simplex", "solver", "linear", "programming")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/coin-or/Clp"
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
    exports_sources = "patches/**.patch"
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("coin-clp does not support shared builds on Windows")
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("coin-utils/2.11.4")
        self.requires("coin-osi/0.108.6")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("Clp-releases-{}".format(self.version), self._source_subfolder)

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "LD": "{} link -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
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
        ]
        self._autotools.configure(configure_dir=os.path.join(self.source_folder, self._source_subfolder), args=configure_args)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        # Installation script expects include/coin to already exist
        tools.mkdir(os.path.join(self.package_folder, "include", "coin"))
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        for l in ("Clp", "ClpSolver", "OsiClp"):
            os.unlink(os.path.join(self.package_folder, "lib", "lib{}.la").format(l))
            if self.settings.compiler == "Visual Studio":
                os.rename(os.path.join(self.package_folder, "lib", "lib{}.a").format(l),
                          os.path.join(self.package_folder, "lib", "{}.lib").format(l))

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["clp"].libs = ["ClpSolver", "Clp"]
        self.cpp_info.components["clp"].includedirs.append(os.path.join("include", "coin"))
        self.cpp_info.components["clp"].names["pkg_config"] = "clp"
        self.cpp_info.components["clp"].requires = ["coin-utils::coin-utils"]

        self.cpp_info.components["osi-clp"].libs = ["OsiClp"]
        self.cpp_info.components["osi-clp"].names["pkg_config"] = "osi-clp"
        self.cpp_info.components["osi-clp"].requires = ["clp", "coin-osi::coin-osi"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
