from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.tools import SystemPackageTool
from conans.errors import ConanInvalidConfiguration
import os


class TinyMidiConan(ConanFile):
    name = "tinymidi"
    description = "A small C library for doing MIDI on GNU/Linux"
    topics = ("conan", "tinymidi", "MIDI")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/krgn/tinymidi"
    license = "LGPL-3.0-only"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("Only Linux is supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
        strip_root=True, destination=self._source_subfolder)

    def _get_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            tools.replace_in_file("Makefile",
                                  "INSTALL_PREFIX=/usr",
                                  "INSTALL_PREFIX=%s" % self.package_folder)
            tools.replace_in_file("Makefile", "COMPILE_FLAGS = ", "COMPILE_FLAGS = $(CFLAGS) ")
            tools.replace_in_file("Makefile", "LINKING_FLAGS = ", "LINKING_FLAGS = $(CFLAGS) ")
            tools.mkdir(os.path.join(self.package_folder, 'include'))
            tools.mkdir(os.path.join(self.package_folder, 'lib'))
            self._get_autotools().make()

    def package(self):
        with tools.chdir(self._source_subfolder):
            self._get_autotools().install()
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self.options.shared:
            os.unlink(os.path.join(self.package_folder, "lib", "libtinymidi.a"))
        else:
            os.unlink(os.path.join(self.package_folder, "lib", "libtinymidi.so"))
            os.unlink(os.path.join(self.package_folder, "lib", "libtinymidi.so.1"))
            os.unlink(os.path.join(self.package_folder, "lib", "libtinymidi.so.1.0.0"))

    def package_info(self):
        self.cpp_info.libs = ["tinymidi"]

