from conans import ConanFile, AutoToolsBuildEnvironment, tools
import contextlib
import os

required_conan_version = ">=1.33.0"


class LibConfuseConan(ConanFile):
    name = "libconfuse"
    description = "Small configuration file parser library for C"
    topics = ("conan", "libconfuse", "configuration", "parser")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinh/libconfuse"
    license = "ISC"
    settings = "os", "arch", "compiler", "build_type"
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.compiler == "Visual Studio" and tools.scm.Version(self.settings.compiler.version) >= "12":
            self._autotools.flags.append("-FS")
        conf_args = []
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(configure_dir=self._source_subfolder, args=conf_args)
        return self._autotools

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                with tools.environment_append({"CC": "cl -nologo",
                                               "CXX": "cl -nologo",
                                               "LD": "link"}):
                    yield
        else:
            yield

    def _patch_sources(self):
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "Makefile.in"),
                              "SUBDIRS = m4 po src $(EXAMPLES) tests doc",
                              "SUBDIRS = m4 src")
        if not self.options.shared:
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "src", "confuse.h"),
                                  "__declspec (dllimport)", "")

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libconfuse.la"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            tools.files.rename(self, os.path.join(self.package_folder, "lib", "confuse.dll.lib"),
                         os.path.join(self.package_folder, "lib", "confuse.lib"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libconfuse"
        self.cpp_info.libs = ["confuse"]
