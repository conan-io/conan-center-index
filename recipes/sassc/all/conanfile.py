from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class SasscConan(ConanFile):
    name = "sassc"
    license = "MIT"
    homepage = "https://sass-lang.com/libsass"
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

    def configure(self):
        if self.settings.os not in ["Linux", "FreeBSD", "Macos"]:
            raise ConanInvalidConfiguration("sassc supports only Linux, FreeBSD and Macos at this time, contributions are welcomed")
            
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        tools.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self.run("autoreconf -fiv", run_environment=True)
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(args=["--disable-tests"])
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

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
