from conans import AutoToolsBuildEnvironment, ConanFile, tools
import contextlib
import os
import shutil

required_conan_version = ">=1.33.0"


class Libatomic_opsConan(ConanFile):
    name = "libatomic_ops"
    homepage = "https://github.com/ivmai/libatomic_ops"
    description = "The atomic_ops project (Atomic memory update operations portable implementation)"
    topics = ("conan", "fmt", "format", "iostream", "printf")
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-2.0-or-later"
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
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def build_requirements(self):
        self.build_requires("gnu-config/cci.20201022")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                with tools.environment_append({"CC": "cl -nologo", "CXX": "cl -nologo",
                                               "LD": "link"}):
                    yield
        else:
            yield

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", None) or self.deps_user_info

    def build(self):
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config.guess"))
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            for lib in ["atomic_ops_gpl", "atomic_ops"]:
                tools.rename(os.path.join(self.package_folder, "lib", "{}.dll.lib".format(lib)),
                             os.path.join(self.package_folder, "lib", "{}.lib".format(lib)))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "atomic_ops"
        self.cpp_info.libs = ["atomic_ops_gpl", "atomic_ops"]
