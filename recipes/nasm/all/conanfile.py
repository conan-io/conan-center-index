import os
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class NASMConan(ConanFile):
    name = "nasm"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.nasm.us"
    description = "The Netwide Assembler, NASM, is an 80x86 and x86-64 assembler"
    license = "BSD-2-Clause"
    settings = "os", "arch", "compiler", "build_type"
    topics = ("conan", "nasm", "installer", "assembler")
    exports_sources = "patches/**"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.which("perl"):
            self.build_requires("strawberryperl/5.30.0.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "nasm-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package_id(self):
        del self.info.settings.compiler

    def _build_vs(self):
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self.settings):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.flags.append("-nologo")
                self.run("nmake /f {} {}".format(os.path.join("Mkfiles", "msvc.mak"), " ".join("{}=\"{}\"".format(k, v) for k, v in autotools.vars.items())))
                shutil.copy("nasm.exe", "nasmw.exe")
                shutil.copy("ndisasm.exe", "ndisasmw.exe")

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            if self.settings.arch == "x86":
                self._autotools.flags.append("-m32")
            elif self.settings.arch == "x86_64":
                self._autotools.flags.append("-m64")
            self._autotools.configure(configure_dir=self._source_subfolder)
            # GCC9 - "pure" attribute on function returning "void"
            tools.replace_in_file("Makefile", "-Werror=attributes", "")
            
            # Need "-arch" flag for the linker when cross-compiling.
            # FIXME: Revisit after https://github.com/conan-io/conan/issues/9069, using new Autotools integration
            if str(self.version).startswith("2.13"):
                tools.replace_in_file("Makefile", "$(CC) $(LDFLAGS) -o", "$(CC) $(ALL_CFLAGS) $(LDFLAGS) -o")

        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)


        if self.settings.os == "Windows":
            self._build_vs()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        if self.settings.os == "Windows":
            self.copy(pattern="*.exe", src=self._source_subfolder, dst="bin", keep_path=False)
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: %s" % bin_path)
        self.env_info.PATH.append(bin_path)
