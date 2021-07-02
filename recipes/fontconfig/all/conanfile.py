import os
import glob

from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class FontconfigConan(ConanFile):
    name = "fontconfig"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Fontconfig is a library for configuring and customizing font access"
    homepage = "https://gitlab.freedesktop.org/fontconfig/fontconfig"
    topics = ("conan", "fontconfig", "fonts", "freedesktop")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio builds are not supported.")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("freetype/2.10.4")
        self.requires("expat/2.4.1")
        if self.settings.os == "Linux":
            self.requires("libuuid/1.0.3")

    def build_requirements(self):
        self.build_requires("gperf/3.1")
        self.build_requires("pkgconf/1.7.4")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            args = ["--enable-static=%s" % ("no" if self.options.shared else "yes"),
                    "--enable-shared=%s" % ("yes" if self.options.shared else "no"),
                    "--disable-docs",
                    "--disable-nls",
                   ]
            args.append("--sysconfdir=%s" % tools.unix_path(os.path.join(self.package_folder, "bin", "etc")))
            args.append("--datadir=%s" % tools.unix_path(os.path.join(self.package_folder, "bin", "share")))
            args.append("--datarootdir=%s" % tools.unix_path(os.path.join(self.package_folder, "bin", "share")))
            args.append("--localstatedir=%s" % tools.unix_path(os.path.join(self.package_folder, "bin", "var")))
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            self._autotools.libs = []
            self._autotools.configure(configure_dir=self._source_subfolder, args=args)
            tools.replace_in_file("Makefile", "po-conf test", "po-conf")
        return self._autotools

    def _patch_files(self):
        #  - fontconfig requires libtool version number, change it for the corresponding freetype one
        tools.replace_in_file(os.path.join(self._source_subfolder, 'configure'), '21.0.15', '2.8.1')
        # disable fc-cache test to enable cross compilation but also builds with shared libraries on MacOS
        tools.replace_in_file(
            os.path.join(self._source_subfolder, 'Makefile.in'),
            '@CROSS_COMPILING_TRUE@RUN_FC_CACHE_TEST = false',
            'RUN_FC_CACHE_TEST=false'
        )

    def build(self):
        # Patch files from dependencies
        self._patch_files()
        with tools.run_environment(self):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with tools.run_environment(self):
            autotools = self._configure_autotools()
            autotools.install()
        os.unlink(os.path.join(self.package_folder, "lib", "libfontconfig.la"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for f in glob.glob(os.path.join(self.package_folder, "bin", "etc", "fonts", "conf.d", "*.conf")):
            if os.path.islink(f):
                os.unlink(f)
        for def_file in glob.glob(os.path.join(self.package_folder, "lib", "*.def")):
            os.remove(def_file)

    def package_info(self):
        self.cpp_info.libs = ["fontconfig"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
        self.cpp_info.names["cmake_find_package"] = "Fontconfig"
        self.cpp_info.names["cmake_find_package_multi"] = "Fontconfig"

        fontconfig_file = os.path.join(self.package_folder, "bin", "etc", "fonts", "fonts.conf")
        self.output.info("Creating FONTCONFIG_FILE environment variable: {}".format(fontconfig_file))
        self.env_info.FONTCONFIG_FILE = fontconfig_file
        fontconfig_path = os.path.join(self.package_folder, "bin", "etc", "fonts")
        self.output.info("Creating FONTCONFIG_PATH environment variable: {}".format(fontconfig_path))
        self.env_info.FONTCONFIG_PATH = fontconfig_path
