from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibuuidConan(ConanFile):
    name = "libuuid"
    description = "Portable uuid C library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/libuuid/"
    license = "BSD-3-Clause"
    topics = ("conan", "libuuid", "uuid", "unique-id", "unique-identifier")
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/**"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _autotools = None

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("libuuid is not supported on Windows")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _configure_autotools(self):
        if not self._autotools:
            configure_args = [
                "--enable-shared=%s" % ("yes" if self.options.shared else "no"),
                "--enable-static=%s" % ("no" if self.options.shared else "yes")
                ]
            self._autotools = AutoToolsBuildEnvironment(self)
            if "x86" in self.settings.arch:
                self._autotools.flags.append('-mstackrealign')
            self._autotools.configure(args=configure_args)
        return self._autotools

    def build(self):
        self._patch_sources()
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
        la_file = os.path.join(self.package_folder, "lib", "libuuid.la")
        if os.path.isfile(la_file):
            os.unlink(la_file)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "uuid"))
