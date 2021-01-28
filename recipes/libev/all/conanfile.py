from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibevConan(ConanFile):
    name = "libev"

    description = "A full-featured and high-performance event loop that is loosely modelled after libevent"
    topics = ("conan", "event", "libev", "event-loop", "periodic-timer", "notify")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://software.schmorp.de/pkg/libev.html"
    license = ["BSD-2-Clause", "GPL-2.0-or-later"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("libev is not supported by Visual Studio")
        if self.settings.os == "Windows" and self.options.shared:
            # libtool:   error: can't build i686-pc-mingw32 shared library unless -no-undefined is specified
            raise ConanInvalidConfiguration("libev can't be built as shared on Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "libev-{0}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows and not os.environ.get("CONAN_BASH_PATH"):
            self.build_requires("msys2/20190524")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        args = []
        if self.options.shared:
            args.extend(['--disable-static', '--enable-shared'])
        else:
            args.extend(['--disable-shared', '--enable-static'])
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, 'share'))
        os.unlink(os.path.join(self.package_folder, "lib", "libev.la"))

    def package_info(self):
        self.cpp_info.libs = ["ev"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
