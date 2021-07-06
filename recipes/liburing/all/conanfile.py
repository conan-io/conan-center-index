import os
import platform

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class LiburingConan(ConanFile):
    name = "liburing"
    license = "GPL-2.0-or-later"
    homepage = "https://github.com/axboe/liburing"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    description = """helpers to setup and
teardown io_uring instances, and also a simplified interface for
applications that don't need (or want) to deal with the full kernel
side implementation."""
    topics = ("asynchronous-io", "async", "kernel")

    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }

    default_options = {
        "fPIC": True,
        "shared": False,
    }

    _autotools = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(configure_dir=self._source_subfolder)
        return self._autotools

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                "liburing is supported only on linux")
        if tools.Version(platform.release()) < "5.1":
            raise ConanInvalidConfiguration(
                "This linux kernel version does not support io uring")

        if self.options.shared:
            del self.options.fPIC

        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            install_args = [
                "ENABLE_SHARED={}".format(1 if self.options.shared else 0)
            ]
            autotools.install(args=install_args)

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "man"))

        if self.options.shared:
            os.remove(os.path.join(self.package_folder, "lib", "liburing.a"))

    def package_info(self):
        self.cpp_info.libs = ["uring"]
