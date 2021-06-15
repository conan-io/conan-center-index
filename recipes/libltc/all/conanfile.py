from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class LibltcConan(ConanFile):
    name = "libltc"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://x42.github.io/libltc/"
    description = "Linear/Logitudinal Time Code (LTC) Library"
    topics = ("timecode", "smpte", "ltc")
    license = "LGPL-3.0"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        }
    default_options = {
        "shared": False,
        "fPIC": True,
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _autotools = None

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        args = []
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

    def package_info(self):
        self.cpp_info.libs = ["ltc"]

