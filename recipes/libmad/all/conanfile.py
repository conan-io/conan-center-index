from conan import ConanFile, tools
from conans import AutoToolsBuildEnvironment, MSBuild
from conan.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.33.0"


class LibmadConan(ConanFile):
    name = "libmad"
    description = "MAD is a high-quality MPEG audio decoder."
    topics = ("conan", "mad", "MPEG", "audio", "decoder")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.underbit.com/products/mad/"
    license = "GPL-2.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.options.shared and self._is_msvc:
            raise ConanInvalidConfiguration("libmad does not support shared library for MSVC")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if not self._is_msvc:
            self.build_requires("gnu-config/cci.20201022")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        if self._is_msvc:
            self._build_msvc()
        else:
            self._build_autotools()

    def _build_msvc(self):
        with tools.files.chdir(self, os.path.join(self._source_subfolder, "msvc++")):
            # cl : Command line error D8016: '/ZI' and '/Gy-' command-line options are incompatible
            tools.files.replace_in_file(self, "libmad.dsp", "/ZI ", "")
            if self.settings.arch == "x86_64":
                tools.files.replace_in_file(self, "libmad.dsp", "Win32", "x64")
                tools.files.replace_in_file(self, "libmad.dsp", "FPM_INTEL", "FPM_DEFAULT")
                tools.files.replace_in_file(self, "mad.h", "# define FPM_INTEL", "# define FPM_DEFAULT")
            with tools.vcvars(self.settings):
                self.run("devenv libmad.dsp /upgrade")
            msbuild = MSBuild(self)
            msbuild.build(project_file="libmad.vcxproj")

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def _build_autotools(self):
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config.guess"))
        autotools = self._configure_autotools()
        autotools.make()

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        args = []
        if self.options.shared:
            args = ["--disable-static", "--enable-shared"]
        else:
            args = ["--disable-shared", "--enable-static"]
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def package(self):
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("CREDITS", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            self.copy(pattern="*.lib", dst="lib", src=self._source_subfolder, keep_path=False)
            self.copy(pattern="mad.h", dst="include", src=os.path.join(self._source_subfolder, "msvc++"))
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = ["libmad" if self._is_msvc else "mad"]
