from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os


class LibTasn1Conan(ConanFile):
    name = "libtasn1"
    homepage = "https://www.gnu.org/software/libtasn1/"
    description = "Libtasn1 is the ASN.1 library used by GnuTLS, p11-kit and some other packages."
    topics = ("conan", "libtasn", "ASN.1", "cryptography")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "arch", "build_type"
    license = "LGPL-2.1-or-later"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
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
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        if "fPIC" in self.options.fields:
            conf_args.append("--with-pic" if self.options.fPIC else "--without-pic")
        autotools.configure(configure_dir=self._source_subfolder, args=conf_args)
        return autotools

    def _patch_sources(self):
        # Do not build executables
        tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile.in"),
                              "\nSUBDIRS = lib src fuzz tests $(am__append_1)",
                              "\nSUBDIRS = lib $(am__append_1)")

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        # tools.rmdir(os.path.join(self.package_folder, "bin"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.remove(os.path.join(self.package_folder, "lib", "libtasn1.la"))

    def package_info(self):
        self.cpp_info.libs = ["tasn1"]
        if not self.options.shared:
            self.cpp_info.defines = ["ASN1_STATIC"]
