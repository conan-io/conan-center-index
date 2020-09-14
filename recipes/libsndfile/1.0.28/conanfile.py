from conans import ConanFile, tools, AutoToolsBuildEnvironment, RunEnvironment
from conans.errors import ConanInvalidConfiguration
import os
import glob


class LibnameConan(ConanFile):
    name = "libsndfile"
    description = "Libsndfile is a library of C routines for reading and writing files containing sampled audio data."
    topics = ("conan", "libsndfile", "sound")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.mega-nerd.com/libsndfile"
    license = "LGPL-2.1"
    generators = 'pkg_config'
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_alsa": [True, False],
        "with_sqlite": [True, False],
        "with_external_libs": [True, False]}
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_alsa": True,
        "with_sqlite": True,
        "with_external_libs": True,}
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.with_alsa:
            self.requires("libalsa/1.1.9")
        if self.options.with_sqlite:
            self.requires("sqlite3/3.29.0")
        if self.options.with_external_libs:
            self.requires("flac/1.3.3")
            self.requires("ogg/1.3.4")
            self.requires("vorbis/1.3.7")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("The project libsndfile can not be built by Visual Studio.")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            args = [
                "--without-caps",
                "--enable-alsa" if self.options.with_alsa else "--disable-alsa",
                "--enable-sqlite" if self.options.with_sqlite else "--disable-sqlite",
                "--enable-external-libs" if self.options.with_external_libs else "--disable-external-libs",
            ]
            if self.options.shared:
                args.extend(['--enable-shared=yes', '--enable-static=no'])
            else:
                args.extend(['--enable-shared=no', '--enable-static=yes'])
            self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with tools.environment_append(RunEnvironment(self).vars):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for f in glob.glob(os.path.join(self.package_folder, "lib", "*.la")):
            os.remove(f)

    def package_info(self):
        self.cpp_info.names['pkg_config'] = 'sndfile'
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "dl", "pthread", "rt"]

