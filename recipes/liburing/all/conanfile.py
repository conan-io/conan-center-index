from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration, ConanException
import os
import re

required_conan_version = ">=1.33.0"


class LiburingConan(ConanFile):
    name = "liburing"
    license = "GPL-2.0-or-later"
    homepage = "https://github.com/axboe/liburing"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("helpers to setup and teardown io_uring instances, and also a simplified interface for "
                   "applications that don't need (or want) to deal with the full kernel side implementation.")
    settings = "os", "compiler", "build_type", "arch"
    topics = ("asynchronous-io", "async", "kernel")

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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _required_glic_version(self):
        return "2.27"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _get_glibc_version(self):
        from six import StringIO
        buffer = StringIO()
        ldd = tools.which("ldd")
        if not ldd:
            raise ConanException("Could not find 'ldd' installed. Please, check your PATH.")
        self.run("{} --version".format(ldd), output=buffer)
        output = buffer.getvalue()
        match = re.search(r'[0-9]+\.[0-9]+', output)
        if not match:
            raise ConanException("Could not parse 'ldd' version. Please, check 'ldd' command.")
        return tools.Version(match.group(0))

    def validate(self):
        # FIXME: use kernel version of build/host machine. kernel version should be encoded in profile
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("liburing is supported only on linux")

        if tools.Version(self.version) >= "2.1" and self._get_glibc_version() < self._required_glic_version:
            raise ConanInvalidConfiguration("glibc {} or higher required to build this package"
                                            .format(self._required_glic_version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure()
        self._autotools.flags.append("-std=gnu99")
        return self._autotools

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
        self.cpp_info.names["pkg_config"] = "liburing"
        self.cpp_info.libs = ["uring"]
