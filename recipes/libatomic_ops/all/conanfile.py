from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import os
import shutil


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
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libatomic_ops-{}".format(self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = []
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
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

        os.unlink(os.path.join(self.package_folder, "lib", "libatomic_ops.la"))
        os.unlink(os.path.join(self.package_folder, "lib", "libatomic_ops_gpl.la"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "atomic_ops"
        libs = ["atomic_ops_gpl", "atomic_ops"]
        if self.settings.os == "Windows" and self.options.shared:
            ext = "lib" if self.settings.compiler == "Visual Studio" else "a"
            libs = list("{}.dll.{}".format(lib, ext) for lib in libs)
        self.cpp_info.libs = libs
