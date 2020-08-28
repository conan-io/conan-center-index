import os
import glob

from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


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
    _source_subfolder = "source_subfolder"
    _autotools = None

    def requirements(self):
        self.requires("freetype/2.10.2")
        self.requires("expat/2.2.9")
        if self.settings.os == "Linux":
            self.requires("libuuid/1.0.3")

    def configure(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows builds are not supported.")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extrated_dir = self.name + "-" + self.version
        os.rename(extrated_dir, self._source_subfolder)

    def build_requirements(self):
        self.build_requires("gperf/3.1")

    def _configure_autotools(self):
        if not self._autotools:
            args = ["--enable-static=%s" % ("no" if self.options.shared else "yes"),
                    "--enable-shared=%s" % ("yes" if self.options.shared else "no"),
                    "--disable-docs"]
            args.append("--sysconfdir=%s" % os.path.join(self.package_folder, "bin", "etc"))
            args.append("--datadir=%s" % os.path.join(self.package_folder, "bin", "share"))
            args.append("--datarootdir=%s" % os.path.join(self.package_folder, "bin", "share"))
            args.append("--localstatedir=%s" % os.path.join(self.package_folder, "bin", "var"))
            self._autotools = AutoToolsBuildEnvironment(self)
            self._autotools.configure(configure_dir=self._source_subfolder, args=args)
            tools.replace_in_file("Makefile", "po-conf test", "po-conf")
        return self._autotools

    def _patch_files(self):
        #  - fontconfig requires libtool version number, change it for the corresponding freetype one
        tools.replace_in_file(os.path.join(self._source_subfolder, 'configure'), '21.0.15', '2.8.1')

    def build(self):
        # Patch files from dependencies
        self._patch_files()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        os.unlink(os.path.join(self.package_folder, "lib", "libfontconfig.la"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for f in glob.glob(os.path.join(self.package_folder, "bin", "etc", "fonts", "conf.d", "*.conf")):
            if os.path.islink(f):
                os.unlink(f)

    def package_info(self):
        self.cpp_info.libs = ["fontconfig"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m", "pthread"])
        self.cpp_info.names["cmake_find_package"] = "Fontconfig"
        self.cpp_info.names["cmake_find_package_multi"] = "Fontconfig"

        self.env_info.FONTCONFIG_FILE = os.path.join(self.package_folder, "bin", "etc", "fonts", "fonts.conf")
        self.env_info.FONTCONFIG_PATH = os.path.join(self.package_folder, "bin", "etc", "fonts")
