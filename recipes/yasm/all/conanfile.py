from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
import os
import shutil


class YASMConan(ConanFile):
    name = "yasm"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yasm/yasm"
    description = "Yasm is a complete rewrite of the NASM assembler under the 'new' BSD License"
    topics = ("conan", "yasm", "installer", "assembler")
    license = "BSD-2-Clause"
    settings = "os", "arch", "compiler", "build_type"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "yasm-%s" % self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.download("https://raw.githubusercontent.com/yasm/yasm/bcc01c59d8196f857989e6ae718458c296ca20e3/YASM-VERSION-GEN.bat",
                       os.path.join(self._source_subfolder, "YASM-VERSION-GEN.bat"))

    @property
    def _msvc_subfolder(self):
        return os.path.join(self._source_subfolder, "Mkfiles", "vc10")

    def _build_vs(self):
        with tools.chdir(self._msvc_subfolder):
            with tools.vcvars(self.settings, force=True):
                msbuild = MSBuild(self)
                if self.settings.arch == "x86":
                    msbuild.build_env.link_flags.append("/MACHINE:X86")
                elif self.settings.arch == "x86_64":
                    msbuild.build_env.link_flags.append("/SAFESEH:NO /MACHINE:X64")
                msbuild.build(project_file="yasm.sln",
                              targets=["yasm"], platforms={"x86": "Win32"}, force_vcvars=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-debug={}".format(yes_no(self.settings.build_type == "Debug")),
            "--disable-rpath",
            "--disable-nls",
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self._build_vs()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="BSD.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            arch = {
                "x86": "Win32",
                "x86_64": "x64",
            }[str(self.settings.arch)]
            tools.mkdir(os.path.join(self.package_folder, "bin"))
            shutil.copy(os.path.join(self._msvc_subfolder, arch, str(self.settings.build_type), "yasm.exe"),
                        os.path.join(self.package_folder, "bin", "yasm.exe"))
            self.copy(pattern="yasm.exe*", src=self._source_subfolder, dst="bin", keep_path=False)
        else:
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
