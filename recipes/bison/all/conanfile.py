
from conans import ConanFile, AutoToolsBuildEnvironment, tools
import glob
import os
import shutil


class ConanFileDefault(ConanFile):
    name = "bison"
    url = "https://github.com/conan-io/conan-center-index   "
    homepage = "https://www.gnu.org/software/bison/"
    description = "Bison is a general-purpose parser generator"
    topics = ("conan", "bison", "parser")
    license = "GPL-3.0-or-later"
    exports_sources = ["patches/*.patch"]
    _source_subfolder = "source_subfolder"
    requires = ("m4/1.4.18", "flex/2.6.4")

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "bison-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        del self.settings.compiler.libcxx

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        self._build_configure()

    def _build_configure(self):
        true = tools.which("true") or "/bin/true"
        args = ["HELP2MAN=%s" % true, "MAKEINFO=%s" % true, "--disable-nls"]
        build = None
        host = None

        env_build = AutoToolsBuildEnvironment(self)
        with tools.chdir(self._source_subfolder):
            tools.replace_in_file("Makefile.in",
                                  "dist_man_MANS = $(top_srcdir)/doc/bison.1",
                                  "dist_man_MANS =")
            tools.replace_in_file(os.path.join("src", "yacc.in"),
                                  "@prefix@",
                                  "${}_ROOT".format(self.name.upper()))
            tools.replace_in_file(os.path.join("src", "yacc.in"),
                                  "@bindir@",
                                  "${}_ROOT/bin".format(self.name.upper()))

            env_build.configure(args=args, build=build, host=host)
            env_build.make()
            env_build.install()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        
        #tools.rmdir(os.path.join(self.package_folder, "share"))
        shutil.move(os.path.join(self.package_folder, "share"), os.path.join(self.package_folder, "bin", "share"))


    def package_info(self):
        self.cpp_info.libs = ["y"]

        self.output.info('Setting BISON_ROOT environment variable: {}'.format(self.package_folder))
        self.env_info.BISON_ROOT = self.package_folder

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)

        bison_pkgdir = os.path.join(self.package_folder, "bin", "share", "bison")
        self.output.info('Setting BISON_INSTALLER_PKGDATADIR environment variable: {}'.format(bison_pkgdir))
        self.env_info.BISON_PKGDATADIR = bison_pkgdir

        self.output.info('Setting BISON_INSTALLER_ROOT environment variable: {}'.format(self.package_folder))
        self.env_info.BISON_INSTALLER_ROOT = self.package_folder
