from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class DdcutilConan(ConanFile):
    name = "ddcutil"
    description = "ddcutil is a Linux program for managing monitor settings, such as brightness, color levels, and input source"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.ddcutil.com/"
    topics = ("ddcutil", "display", "monitor", "settings", "linux")
    license = "GPL-2.0-or-later"
    
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = ["patches/*"]
    generators = "pkg_config"
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
        self.requires("glib/2.70.1")
        self.requires("i2c-tools/4.3")
        self.requires("libdrm/2.4.109")
        self.requires("libkmod/system")
        self.requires("libudev/system")
        self.requires("libusb/1.0.24")
        self.requires("xorg/system")
        self.requires("zlib/1.2.11")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("ddcutil is only available for Linux")

    def build_requirements(self):
        self.build_requires("autoconf/2.71")
        self.build_requires("automake/1.16.4")
        self.build_requires("libtool/2.4.6")
        self.build_requires("m4/1.4.19")
        self.build_requires("pkgconf/1.7.4")    
    
    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def system_requirements(self):
        packages = []
        if tools.os_info.is_linux and self.settings.os == "Linux":
            if tools.os_info.with_yum:
                packages = ["hwdata", "libgudev"]
            elif tools.os_info.with_apt:
                packages = ["hwdata", "libgudev-1.0-dev"]
            elif tools.os_info.with_pacman:
                packages = ["hwids", "libgudev"]
            elif tools.os_info.with_zypper:
                packages = ["hwdata", "libgudev-1_0-0"]
            else:
                self.output.warn("Don't know how to install %s for your distro." % self.name)
        if packages:
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode='verify')
            for p in packages:
                package_tool.install(update=True, packages=p)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        conf_args = []
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        with tools.environment_append(tools.RunEnvironment(self).vars):
            self._autotools.configure(configure_dir=self._source_subfolder, args=conf_args)
        return self._autotools

    def build(self):
        for patch in self.conan_data["patches"].get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")))
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        if not self.options.shared and tools.Version(self.version) <= "1.2.2":
            # see https://github.com/rockowitz/ddcutil/issues/242
            self.copy("*/libddcutil.a", dst="lib", src="./", keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread"])
