from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class ScdocInstallerConan(ConanFile):
    name = "scdoc"
    description = "scdoc is a simple man page generator for POSIX systems written in C99."
    topics = ("manpage", "documentation", "posix")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git.sr.ht/~sircmpwn/scdoc"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        self.build_requires("make/4.3")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        with tools.chdir(self._source_subfolder):
            autotools.make()

    def package(self):
        autotools = self._configure_autotools()
        with tools.chdir(self._source_subfolder):
            autotools.install(args=[f"PREFIX={self.package_folder}"])
        self.copy(pattern="COPYING", dst="licenses",
                  src=self._source_subfolder)
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libdirs = []

        scdoc_root = os.path.join(self.package_folder, "bin")
        self.output.info(
            "Appending PATH environment variable: {}".format(scdoc_root))
        self.env_info.PATH.append(scdoc_root)
        self._chmod_plus_x(os.path.join(scdoc_root, "scdoc"))
        pkgconfig_variables = {
            'exec_prefix': '${prefix}/bin',
            'scdoc': '${exec_prefix}/scdoc',
        }
        self.cpp_info.set_property(
            "pkg_config_custom_content",
            "\n".join("%s=%s" % (key, value) for key,value in pkgconfig_variables.items()))

    def validate(self):
        if self.settings.os in ["Macos", "Windows"]:
            raise ConanInvalidConfiguration(
                f"Builds aren't supported on {self.settings.os}")
