from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os


class LibalsaConan(ConanFile):
    name = "libalsa"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alsa-project/alsa-lib"
    topics = ("conan", "libalsa", "alsa", "sound", "audio", "midi")
    description = "Library of ALSA: The Advanced Linux Sound Architecture, that provides audio " \
                  "and MIDI functionality to the Linux operating system"
    options = {"shared": [True, False], "fPIC": [True, False], "disable_python": [True, False]}
    default_options = {'shared': False, 'fPIC': True, 'disable_python': True}
    settings = "os", "compiler", "build_type", "arch"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux supported")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("alsa-lib-{}".format(self.version), self._source_subfolder)

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def _configure_autotools(self):
        if not self._autotools:
            self.run("touch ltconfig", run_environment=True)
            self.run("libtoolize --force --copy --automake", run_environment=True)
            self.run("aclocal $ACLOCAL_FLAGS", run_environment=True)
            self.run("autoheader", run_environment=True)
            self.run("automake --foreign --copy --add-missing", run_environment=True)
            self.run("touch depcomp", run_environment=True)
            self.run("autoconf", run_environment=True)

            self._autotools = AutoToolsBuildEnvironment(self)
            args = ["--enable-static=yes", "--enable-shared=no"] \
                    if not self.options.shared else ["--enable-static=no", "--enable-shared=yes"]
            args.append("--datarootdir=%s" % os.path.join(self.package_folder, "res"))
            if self.options.disable_python:
                args.append("--disable-python")
            self._autotools.configure(args=args)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))        
        for l in ["asound", "atopology"]:
            la_file = os.path.join(self.package_folder, "lib", "lib%s.la" % l)
            if os.path.isfile(la_file):
                os.unlink(la_file)

    def package_info(self):
        self.cpp_info.libs = ["asound"]
        self.cpp_info.system_libs = ["dl", "m", "rt", "pthread"]
        self.cpp_info.names['pkg_config'] = 'alsa'
        self.cpp_info.names["cmake_find_package"] = "ALSA"
        self.cpp_info.names["cmake_find_package_multi"] = "ALSA"
        self.env_info.ALSA_CONFIG_DIR = os.path.join(self.package_folder, "res", "alsa")
