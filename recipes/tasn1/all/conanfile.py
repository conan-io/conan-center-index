from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os


class Tasn1Conan(ConanFile):
    name = "tasn1"
    homepage = "https://www.gnu.org/software/libtasn1/"
    description = "Libtasn1 is the ASN.1 library used by GnuTLS, p11-kit and some other packages."
    topics = ("conan", "libtasn", "ASN.1", "cryptography")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os_build", "arch_build", "compiler"
    license = "LGPL-2.1-or-later"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio is unsupported by libtasn1")
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        self.build_requires("bison_installer/3.3.2@bincrafters/stable")
        if tools.os_info.is_windows and os.environ.get("CONAN_BASH_PATH", None) is None:
            self.build_requires("msys/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = os.path.join("libtasn1-" + self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--disable-doc",
        ]
        conf_args.extend(["--disable-shared", "--enable-static"])
        autotools.configure(configure_dir=self._source_subfolder, args=conf_args)
        return autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package_id(self):
        del self.info.settings.compiler
        self.info.include_build_settings()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "include"))
        tools.rmdir(os.path.join(self.package_folder, "lib"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: %s" % (bin_path))
        self.env_info.PATH.append(bin_path)
