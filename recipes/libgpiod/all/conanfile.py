from conan import ConanFile, tools
from conans import AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class LibgpiodConan(ConanFile):
    name = "libgpiod"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/"
    license = "LGPL-2.1-or-later"
    description = "C library and tools for interacting with the linux GPIO character device"
    topics = ("gpio", "libgpiod", "libgpiodcxx", "linux")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_bindings_cxx": [True, False],
        "enable_tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_bindings_cxx": False,
        "enable_tools": False,
    }
    
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("libgpiod supports only Linux")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.enable_bindings_cxx:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        self.build_requires("pkgconf/1.7.4")
        self.build_requires("autoconf-archive/2021.02.19")
        self.build_requires("linux-headers-generic/5.13.9")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
                return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-bindings-cxx={}".format(yes_no(self.options.enable_bindings_cxx)),
            "--enable-tools={}".format(yes_no(self.options.enable_tools)),
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with tools.files.chdir(self, os.path.join(self._source_subfolder)):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.files.rm(self, "*.la", self.package_folder)
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["gpiod"].libs = ["gpiod"]
        self.cpp_info.components["gpiod"].names["pkg_config"] = "gpiod"
        if self.options.enable_bindings_cxx:
            self.cpp_info.components["gpiodcxx"].libs = ["gpiodcxx"]
            self.cpp_info.components["gpiodcxx"].names["pkg_config"] = "gpiodcxx"
            self.cpp_info.components["gpiodcxx"].requires = ["gpiod"]
