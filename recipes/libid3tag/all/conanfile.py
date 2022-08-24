from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conan.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.33.0"


class LibId3TagConan(ConanFile):
    name = "libid3tag"
    description = "ID3 tag manipulation library."
    topics = ("conan", "mad", "id3", "MPEG", "audio", "decoder")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.underbit.com/products/mad/"
    license = "GPL-2.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generator = "pkg_config", "visual_studio"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("zlib/1.2.11")

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio" or (
            self.settings.compiler == "clang" and self.settings.os == "Windows"
        )

    def validate(self):
        if self._is_msvc and self.options.shared:
            raise ConanInvalidConfiguration("libid3tag does not support shared library for MSVC")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if not self._is_msvc:
            self.build_requires("gnu-config/cci.20201022")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        if self._is_msvc:
            self._build_msvc()
        else:
            self._build_autotools()

    def _build_msvc(self):
        kwargs = {}
        with tools.chdir(os.path.join(self._source_subfolder, "msvc++")):
            # cl : Command line error D8016: '/ZI' and '/Gy-' command-line options are incompatible
            tools.replace_in_file("libid3tag.dsp", "/ZI ", "")
            if self.settings.compiler == "clang":
                tools.replace_in_file("libid3tag.dsp", "CPP=cl.exe", "CPP=clang-cl.exe")
                tools.replace_in_file("libid3tag.dsp", "RSC=rc.exe", "RSC=llvm-rc.exe")
                kwargs["toolset"] = "ClangCl"
            if self.settings.arch == "x86_64":
                tools.replace_in_file("libid3tag.dsp", "Win32", "x64")
            with tools.vcvars(self.settings):
                self.run("devenv /Upgrade libid3tag.dsp")
            msbuild = MSBuild(self)
            msbuild.build(project_file="libid3tag.vcxproj", **kwargs)

    def _configure_autotools(self):
        if not self._autotools:
            if self.options.shared:
                args = ["--disable-static", "--enable-shared"]
            else:
                args = ["--disable-shared", "--enable-static"]
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

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

    def _install_autotools(self):
        autotools = self._configure_autotools()
        autotools.install()
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package(self):
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("CREDITS", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            self.copy(pattern="*.lib", dst="lib", src=self._source_subfolder, keep_path=False)
            self.copy(pattern="id3tag.h", dst="include", src=self._source_subfolder)
        else:
            self._install_autotools()

    def package_info(self):
        self.cpp_info.libs = ["libid3tag" if self._is_msvc else "id3tag"]
