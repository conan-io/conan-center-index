import os
import shutil

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration


class LiburingConan(ConanFile):
    name = "liburing"
    license = "GPL-2.0-or-later"
    author = "Ilya Kazakov kazakovilya97@gmail.com"
    homepage = "https://github.com/axboe/liburing"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }

    default_options = {
        "fPIC": True,
        "shared": False,
    }

    _autotools = None

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(self)
        prefix = self.package_folder
        conf_args = [
            "--prefix={}".format(prefix),
        ]
        self._autotools.configure(
            args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(f"{self.name}-{self.name}-{self.version}",
                  self._source_subfolder)

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                "liburing is supported only on linux")

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
                f"ENABLE_SHARED={1 if self.options.shared else 0}"
            ]
            autotools.install(args=install_args)

        shutil.rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))
        shutil.rmtree(os.path.join(self.package_folder, "man"))

        if self.options.shared:
            os.remove(os.path.join(self.package_folder, "lib", "liburing.a"))
            os.remove(os.path.join(self.package_folder, "lib", "liburing.so"))
            with tools.chdir(os.path.join(self.package_folder, "lib")):
                os.symlink("liburing.so.1", "liburing.so")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
