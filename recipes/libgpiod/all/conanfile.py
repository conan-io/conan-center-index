from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os
import platform
import re

required_conan_version = ">=1.33.0"

class LibgpiodConan(ConanFile):
    name = "libgpiod"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/"
    license = "LGPL-2.1-or-later"
    description = "C library and tools for interacting with the linux GPIO character device"
    topics = ("conan", "gpio", "libgpiod", "libgpiodcxx", "linux")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "enable_bindings_cxx": [True, False],
               "enable_tools": [True, False]}
    default_options = {"shared": False,
                       "enable_bindings_cxx": False,
                       "enable_tools": False}
    
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("only Linux is supported")
        linux_kernel_version = re.match("([0-9.]+)", platform.release()).group(1)
        if tools.Version(linux_kernel_version) < "4.8":
            raise ConanInvalidConfiguration("only Linux kernel versions >= 4.8 are supported")

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        self.build_requires("pkgconf/1.7.4")
        self.build_requires("autoconf-archive/2021.02.19")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if not self._autotools:
            args = []
            if self.options.shared:
                args.extend(["--disable-static", "--enable-shared"])
            else:
                args.extend(["--disable-shared", "--enable-static"])
            if self.options.enable_bindings_cxx:
                args.extend(["--enable-bindings-cxx"])
            if self.options.enable_tools:
                args.extend(["--enable-tools"])
            self._autotools = AutoToolsBuildEnvironment(self)
            self._autotools.configure(args=args)
        return self._autotools

    def build(self):
        with tools.chdir(os.path.join(self._source_subfolder)):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True)
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with tools.chdir(os.path.join(self._source_subfolder)):
            autotools = self._configure_autotools()
            autotools.install()
        tools.remove_files_by_mask(self.package_folder, "*.la")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["gpiodcxx", "gpiod"]
