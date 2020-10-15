from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os


class CoinOsiConan(ConanFile):
    name = "coin-osi"
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
            raise ConanInvalidConfiguration("coin-osi does not support shared builds on Windows")
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("coin-utils/2.11.4")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.3")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("Osi-releases-{}".format(self.version), self._source_subfolder)

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                    "LD": "link -nologo",
                    "AR": "lib",
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
            "--without-blas"
            "--without-lapack"
        ]
        if self.settings.compiler == "Visual Studio":
            self._autotools.cxx_flags.append("-EHsc")
            configure_args.append("--enable-msvc={}".format(self.settings.compiler.runtime))
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
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libOsi.la"))
        os.unlink(os.path.join(self.package_folder, "lib", "libOsiCommonTests.la"))

        if self.settings.compiler == "Visual Studio":
            for l in ("Osi", "OsiCommonTests"):
                os.rename(os.path.join(self.package_folder, "lib", "lib{}.lib").format(l),
                          os.path.join(self.package_folder, "lib", "{}.lib").format(l))

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["libosi"].libs = ["Osi"]
        self.cpp_info.components["libosi"].includedirs = [os.path.join("include", "coin")]
        self.cpp_info.components["libosi"].requires = ["coin-utils::coin-utils"]
        self.cpp_info.components["libosi"].names["pkg_config"] = "osi"

        self.cpp_info.components["osi-unittests"].libs = ["OsiCommonTests"]
        self.cpp_info.components["osi-unittests"].requires = ["libosi"]
        self.cpp_info.components["osi-unittests"].names["pkg_config"] = "osi-unittests"
