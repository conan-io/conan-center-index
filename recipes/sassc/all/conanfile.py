from conans import ConanFile, AutoToolsBuildEnvironment, tools


class SasscConan(ConanFile):
    name = "sassc"
    license = "MIT"
    homepage = "libsass.org"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libsass command line driver"
    topics = ("Sass", "sassc", "compiler")
    settings = "os", "compiler", "build_type", "arch"

    build_requires = "autoconf/2.69", "libtool/2.4.6"

    requires = "libsass/3.6.4"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        tools.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self.run("autoreconf -fiv", run_environment=True)
        self._autotools = AutoToolsBuildEnvironment(self)
        args = []
        args.append("--disable-tests")
        self._autotools.configure(args=args)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            tools.save(path="VERSION", content="%s" % self.version)
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
