from conans import AutoToolsBuildEnvironment, tools
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, rmdir, chdir
import os

required_conan_version = ">=1.47.0"


class Asn1cConan(ConanFile):
    name = "asn1c"
    description = "The ASN.1 Compiler"
    license = "BSD-2-Clause"
    topics = ("asn.1", "compiler")
    homepage = "https://lionet.info/asn1c"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "res")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.tool_requires("bison/3.7.6")
        self.tool_requires("flex/2.6.4")
        self.tool_requires("libtool/2.4.7")

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio is not supported")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
                "--datarootdir={}".format(tools.unix_path(self._datarootdir)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with chdir(self, self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "res", "doc"))
        rmdir(self, os.path.join(self.package_folder, "res", "man"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        # asn1c cannot use environment variables to specify support files path
        # so `SUPPORT_PATH` should be propagated to command line invocation to `-S` argument
        self.env_info.SUPPORT_PATH = os.path.join(self.package_folder, "res/asn1c")

        self.cpp_info.includedirs = []
