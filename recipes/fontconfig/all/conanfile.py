from conans import ConanFile, tools, AutoToolsBuildEnvironment, Meson
from conans.errors import ConanInvalidConfiguration
import contextlib
import functools
import os

required_conan_version = ">=1.33.0"


class FontconfigConan(ConanFile):
    name = "fontconfig"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Fontconfig is a library for configuring and customizing font access"
    homepage = "https://gitlab.freedesktop.org/fontconfig/fontconfig"
    topics = ("fonts", "freedesktop")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "patches/*"
    generators = "pkg_config"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("freetype/2.11.0")
        self.requires("expat/2.4.1")
        if self.settings.os == "Linux":
            self.requires("libuuid/1.0.3")

    def build_requirements(self):
        self.build_requires("gperf/3.1")
        self.build_requires("pkgconf/1.7.4")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("meson/0.59.1")
        else:
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def validate(self):
        if self.settings.compiler == "Visual Studio" and tools.Version(self.version) < "2.13.93":
            raise ConanInvalidConfiguration("fontconfig does not support Visual Studio for versions < 2.13.93.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--disable-docs",
            "--disable-nls",
            "--sysconfdir={}".format(tools.unix_path(os.path.join(self.package_folder, "bin", "etc"))),
            "--datadir={}".format(tools.unix_path(os.path.join(self.package_folder, "bin", "share"))),
            "--datarootdir={}".format(tools.unix_path(os.path.join(self.package_folder, "bin", "share"))),
            "--localstatedir={}".format(tools.unix_path(os.path.join(self.package_folder, "bin", "var"))),
        ]
        autotools.configure(configure_dir=self._source_subfolder, args=args)
        tools.replace_in_file("Makefile", "po-conf test", "po-conf")
        return autotools

    @functools.lru_cache(1)
    def _configure_meson(self):
        meson = Meson(self)
        meson.options["doc"] = "disabled"
        meson.options["nls"] = "disabled"
        meson.options["tests"] = "disabled"
        meson.options["tools"] = "disabled"
        meson.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return meson

    def _patch_files(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # fontconfig requires libtool version number, change it for the corresponding freetype one
        tools.replace_in_file(os.path.join(self.install_folder, "freetype2.pc"),
                              "Version: {}".format(self.deps_cpp_info["freetype"].version),
                              "Version: {}".format(self.deps_user_info["freetype"].LIBTOOL_VERSION))
        # disable fc-cache test to enable cross compilation but also builds with shared libraries on MacOS
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "Makefile.in"),
            "@CROSS_COMPILING_TRUE@RUN_FC_CACHE_TEST = false",
            "RUN_FC_CACHE_TEST=false"
        )

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "cl",
                    "CXX": "cl",
                    "LD": "link",
                    "AR": "lib",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def build(self):
        self._patch_files()
        if self.settings.compiler == "Visual Studio":
            with self._build_context():
                meson = self._configure_meson()
                meson.build()
        else:
            with tools.run_environment(self):
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            with self._build_context():
                meson = self._configure_meson()
                meson.install()
                if os.path.isfile(os.path.join(self.package_folder, "lib", "libfontconfig.a")):
                    tools.rename(os.path.join(self.package_folder, "lib", "libfontconfig.a"),
                                 os.path.join(self.package_folder, "lib", "fontconfig.lib"))
        else:
            with tools.run_environment(self):
                autotools = self._configure_autotools()
                autotools.install()
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin", "etc", "fonts", "conf.d"), "*.conf")
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.def")
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["fontconfig"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["m", "pthread"])
        self.cpp_info.names["cmake_find_package"] = "Fontconfig"
        self.cpp_info.names["cmake_find_package_multi"] = "Fontconfig"
        self.cpp_info.names["pkg_config"] = "fontconfig"

        fontconfig_file = os.path.join(self.package_folder, "bin", "etc", "fonts", "fonts.conf")
        self.output.info("Creating FONTCONFIG_FILE environment variable: {}".format(fontconfig_file))
        self.env_info.FONTCONFIG_FILE = fontconfig_file
        fontconfig_path = os.path.join(self.package_folder, "bin", "etc", "fonts")
        self.output.info("Creating FONTCONFIG_PATH environment variable: {}".format(fontconfig_path))
        self.env_info.FONTCONFIG_PATH = fontconfig_path
