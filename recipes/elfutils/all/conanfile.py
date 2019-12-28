from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class ElfutilsConan(ConanFile):
    name = "elfutils"
    description = "A dwarf, dwfl and dwelf functions to read DWARF, find separate debuginfo, symbols and inspect process state."
    homepage = "https://sourceware.org/elfutils"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "elfutils", "libelf", "libdw", "libasm")
    license = "MIT"
    exports = ["LICENSE.md", "patches/elfutils-*.patch"]
    autotools = None

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {'fPIC': True}
    requires = (
        "bzip2/1.0.6",
        "zlib/1.2.11",
        "xz_utils/5.2.4"
    )

    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "elfutils" + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self.autotools:
            args = ['--enable-silent-rules', '--with-zlib', '--with-bzlib', '--with-lzma']
            self.autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            self.autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self.autotools

    def build(self):
        tools.patch(**self.conan_data["patches"][self.version])
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING*", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        #tools.rmdir(os.path.join(self.package_folder, "bin"))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)