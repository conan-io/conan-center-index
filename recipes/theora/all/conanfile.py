import os
import shutil
import stat
from conans import ConanFile, MSBuild, AutoToolsBuildEnvironment, tools

required_conan_version = ">=1.33.0"


class TheoraConan(ConanFile):
    name = "theora"
    description = "Theora is a free and open video compression format from the Xiph.org Foundation"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/theora"
    topics = ("conan", "theora", "video", "video-compressor", "video-format")
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("ogg/1.3.4")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            self.build_requires("gnu-config/cci.20201022")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][0], strip_root=True, destination=self._source_subfolder)

        source = self.conan_data["sources"][self.version][1]
        url = source["url"]
        filename = url[url.rfind("/") + 1:]
        tools.download(url, filename)
        tools.check_sha256(filename, source["sha256"])

        shutil.move(filename, os.path.join(self._source_subfolder, 'lib', filename))

    def _build_msvc(self):
        def format_libs(libs):
            return " ".join([l + ".lib" for l in libs])

        project = "libtheora"
        config = "dynamic" if self.options.shared else "static"
        vcvproj_dir = os.path.join(self._source_subfolder, "win32", "VS2008", project)
        vcvproj = "{}_{}.vcproj".format(project, config)

        # fix hard-coded ogg names
        vcvproj_path = os.path.join(vcvproj_dir, vcvproj)
        if self.options.shared:
            tools.replace_in_file(vcvproj_path,
                                  "libogg.lib",
                                  format_libs(self.deps_cpp_info["ogg"].libs))
        if "MT" in self.settings.compiler.runtime:
            tools.replace_in_file(vcvproj_path, 'RuntimeLibrary="2"', 'RuntimeLibrary="0"')
            tools.replace_in_file(vcvproj_path, 'RuntimeLibrary="3"', 'RuntimeLibrary="1"')

        with tools.chdir(vcvproj_dir):
            msbuild = MSBuild(self)
            msbuild.build(vcvproj, platforms={"x86": "Win32", "x86_64": "x64"})

    def _configure_autotools(self):
        if not self._autotools:
            permission = stat.S_IMODE(os.lstat("configure").st_mode)
            os.chmod("configure", (permission | stat.S_IEXEC))
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            configure_args = ['--disable-examples']
            if self.options.shared:
                configure_args.extend(['--disable-static', '--enable-shared'])
            else:
                configure_args.extend(['--disable-shared', '--enable-static'])
            self._autotools.configure(args=configure_args)
        return self._autotools

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            self._build_msvc()
        else:
            shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                        os.path.join(self._source_subfolder, "config.sub"))
            shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                        os.path.join(self._source_subfolder, "config.guess"))
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == 'Visual Studio':
            include_folder = os.path.join(self._source_subfolder, "include")
            self.copy(pattern="*.h", dst="include", src=include_folder)
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
        else:
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.install()
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
