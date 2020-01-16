from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibUnistringConan(ConanFile):
    name = "libunistring"
    description = "This library provides functions for manipulating Unicode strings and for manipulating C strings according to the Unicode standard."
    homepage = "https://www.gnu.org/software/libunistring/"
    topics = ("conan", "libunistring", "unicode", "string")
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _source_subfolder = "source_subfolder"
    _autotools = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio is unsupported")
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Shared build on Windows is not supported")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libunistring-{}".format(self.version), self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows and not "CONAN_BASH_PATH" in os.environ:
            self.build_requires("msys2/20190524")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = []
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])

        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING*", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libunistring.la"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["unistring"]
