import os
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class NASMConan(ConanFile):
    name = "nasm"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.nasm.us"
    description = "The Netwide Assembler, NASM, is an 80x86 and x86-64 assembler"
    license = "BSD-2-Clause"
    settings = "os_build", "arch_build", "compiler"
    topics = ("conan", "nasm", "installer", "assembler")
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self.settings.os_build == "Windows" and not tools.which("perl"):
            self.build_requires("strawberryperl/5.30.0.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "nasm-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _build_vs(self):
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self.settings, arch=str(self.settings.arch_build), force=True):
                self.run("nmake /f {}".format(os.path.join("Mkfiles", "msvc.mak")))
                shutil.copy('nasm.exe', 'nasmw.exe')
                shutil.copy('ndisasm.exe', 'ndisasmw.exe')

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            if self.settings.arch_build == "x86":
                self._autotools.flags.append("-m32")
            elif self.settings.arch_build == "x86_64":
                self._autotools.flags.append("-m64")
            self._autotools.configure(configure_dir=self._source_subfolder)
            # GCC9 - 'pure' attribute on function returning 'void'
            tools.replace_in_file("Makefile", "-Werror=attributes", "")
        return self._autotools

    def _build_configure(self):
        autotools = self._configure_autotools()
        autotools.make()

    def build(self):
        if self.settings.os_build == 'Windows':
            self._build_vs()
        else:
            self._build_configure()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        if self.settings.os_build == 'Windows':
            self.copy(pattern='*.exe', src=self._source_subfolder, dst='bin', keep_path=False)
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, 'bin')
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.PATH.append(bin_path)
