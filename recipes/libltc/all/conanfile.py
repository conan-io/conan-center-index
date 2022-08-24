from conans import ConanFile, AutoToolsBuildEnvironment, tools
import contextlib
import os

required_conan_version = ">=1.33.0"


class LibltcConan(ConanFile):
    name = "libltc"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://x42.github.io/libltc/"
    description = "Linear/Logitudinal Time Code (LTC) Library"
    topics = ("timecode", "smpte", "ltc")
    license = "LGPL-3.0"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.3")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "{} cl -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                    "LD": "{} link -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                    "AR": "{} lib".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].ar_lib)),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        if self.settings.compiler == "Visual Studio":
            self._autotools.cxx_flags.append("-EHsc")
            if tools.Version(self.settings.compiler.version) >= "12":
                self._autotools.flags.append("-FS")
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.unlink(os.path.join(self.package_folder, "lib", "libltc.la"))
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            tools.files.rename(self, os.path.join(self.package_folder, "lib", "ltc.dll.lib"),
                    os.path.join(self.package_folder, "lib", "ltc.lib"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "ltc"
        self.cpp_info.libs = ["ltc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
