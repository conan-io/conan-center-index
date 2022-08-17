from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import files, scm
from conans import tools, AutoToolsBuildEnvironment, Meson
import contextlib
import functools
import os

required_conan_version = ">=1.50.2"


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

    generators = "pkg_config"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("freetype/2.12.1")
        self.requires("expat/2.4.8")
        if self.settings.os == "Linux":
            self.requires("libuuid/1.0.3")

    def validate(self):
        if self._is_msvc and scm.Version(self.version) < "2.13.93":
            raise ConanInvalidConfiguration("fontconfig does not support Visual Studio for versions < 2.13.93.")

    def build_requirements(self):
        self.build_requires("gperf/3.1")
        self.build_requires("pkgconf/1.7.4")
        if self._is_msvc:
            self.build_requires("meson/0.63.1")
        elif self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

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
        files.apply_conandata_patches(self)
        # fontconfig requires libtool version number, change it for the corresponding freetype one
        files.replace_in_file(self, os.path.join(self.install_folder, "freetype2.pc"),
                              "Version: {}".format(self.deps_cpp_info["freetype"].version),
                              "Version: {}".format(self.deps_user_info["freetype"].LIBTOOL_VERSION))
        # disable fc-cache test to enable cross compilation but also builds with shared libraries on MacOS
        files.replace_in_file(self,
            os.path.join(self._source_subfolder, "Makefile.in"),
            "@CROSS_COMPILING_TRUE@RUN_FC_CACHE_TEST = false",
            "RUN_FC_CACHE_TEST=false"
        )

    @contextlib.contextmanager
    def _build_context(self):
        if self._is_msvc:
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
        if self._is_msvc:
            with self._build_context():
                meson = self._configure_meson()
                meson.build()
        else:
            # relocatable shared lib on macOS
            files.replace_in_file(self,
                os.path.join(self._source_subfolder, "configure"),
                "-install_name \\$rpath/",
                "-install_name @rpath/"
            )
            with tools.run_environment(self):
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        if self._is_msvc:
            with self._build_context():
                meson = self._configure_meson()
                meson.install()
                if os.path.isfile(os.path.join(self.package_folder, "lib", "libfontconfig.a")):
                    files.rename(self, os.path.join(self.package_folder, "lib", "libfontconfig.a"),
                                 os.path.join(self.package_folder, "lib", "fontconfig.lib"))
        else:
            with tools.run_environment(self):
                autotools = self._configure_autotools()
                autotools.install()
        files.rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        files.rm(self, "*.conf", os.path.join(self.package_folder, "bin", "etc", "fonts", "conf.d"))
        files.rm(self, "*.def", os.path.join(self.package_folder, "lib"))
        files.rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        files.rmdir(self, os.path.join(self.package_folder, "etc"))
        files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Fontconfig")
        self.cpp_info.set_property("cmake_target_name", "Fontconfig::Fontconfig")
        self.cpp_info.set_property("pkg_config_name", "fontconfig")
        self.cpp_info.libs = ["fontconfig"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["m", "pthread"])

        self.cpp_info.names["cmake_find_package"] = "Fontconfig"
        self.cpp_info.names["cmake_find_package_multi"] = "Fontconfig"

        fontconfig_file = os.path.join(self.package_folder, "bin", "etc", "fonts", "fonts.conf")
        self.output.info(f"Creating FONTCONFIG_FILE environment variable: {fontconfig_file}")
        self.runenv_info.prepend_path("FONTCONFIG_FILE", fontconfig_file)
        self.env_info.FONTCONFIG_FILE = fontconfig_file # TODO: remove in conan v2?

        fontconfig_path = os.path.join(self.package_folder, "bin", "etc", "fonts")
        self.output.info(f"Creating FONTCONFIG_PATH environment variable: {fontconfig_path}")
        self.runenv_info.prepend_path("FONTCONFIG_PATH", fontconfig_path)
        self.env_info.FONTCONFIG_PATH = fontconfig_path # TODO: remove in conan v2?
