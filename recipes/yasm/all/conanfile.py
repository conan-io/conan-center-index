from conan import ConanFile, tools
from conans import AutoToolsBuildEnvironment, MSBuild
import os
import shutil

required_conan_version = ">=1.33.0"


class YASMConan(ConanFile):
    name = "yasm"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yasm/yasm"
    description = "Yasm is a complete rewrite of the NASM assembler under the 'new' BSD License"
    topics = ("yasm", "installer", "assembler")
    license = "BSD-2-Clause"
    settings = "os", "arch", "compiler", "build_type"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self._settings_build.os == "Windows" and self.settings.compiler != "Visual Studio" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version][0],
                  destination=self._source_subfolder, strip_root=True)
        tools.files.download(self, **self.conan_data["sources"][self.version][1],
                       filename=os.path.join(self._source_subfolder, "YASM-VERSION-GEN.bat"))

    @property
    def _msvc_subfolder(self):
        return os.path.join(self._source_subfolder, "Mkfiles", "vc10")

    def _build_vs(self):
        with tools.files.chdir(self, self._msvc_subfolder):
            msbuild = MSBuild(self)
            if self.settings.arch == "x86":
                msbuild.build_env.link_flags.append("/MACHINE:X86")
            elif self.settings.arch == "x86_64":
                msbuild.build_env.link_flags.append("/SAFESEH:NO /MACHINE:X64")
            build_type = "Debug" if self.settings.build_type == "Debug" else "Release"
            msbuild.build(project_file="yasm.sln", build_type=build_type, upgrade_project=False,
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
            tools.files.mkdir(self, os.path.join(self.package_folder, "bin"))
            build_type = "Debug" if self.settings.build_type == "Debug" else "Release"
            shutil.copy(os.path.join(self._msvc_subfolder, arch, build_type, "yasm.exe"),
                        os.path.join(self.package_folder, "bin", "yasm.exe"))
            self.copy(pattern="yasm.exe*", src=self._source_subfolder, dst="bin", keep_path=False)
        else:
            autotools = self._configure_autotools()
            autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
