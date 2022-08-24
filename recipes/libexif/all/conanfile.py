from conans import ConanFile, tools, AutoToolsBuildEnvironment
import contextlib
import os

required_conan_version = ">=1.33.0"


class LibexifConan(ConanFile):
    name = "libexif"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libexif.github.io/"
    license = "LGPL-2.1"
    description = "libexif is a library for parsing, editing, and saving EXIF data."
    topics = ("exif", "metadata", "parse", "edit")
    exports_sources = "patches/*"
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

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "cl -nologo",
                    "AR": "lib",
                    "LD": "link -nologo",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("gettext/0.21")
        self.build_requires("libtool/2.4.6")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
        self._autotools.libs = []
        if self.settings.compiler == "Visual Studio" and tools.scm.Version(self, self.settings.compiler.version) >= "12":
            self._autotools.flags.append("-FS")
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--disable-docs",
            "--disable-nls",
            "--disable-rpath",
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            tools.files.rename(self, os.path.join(self.package_folder, "lib", "exif.dll.lib"),
                         os.path.join(self.package_folder, "lib", "exif.lib"))
        tools.files.rm(self, self.package_folder, "*.la")
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["exif"]
        self.cpp_info.names["pkg_config"] = "libexif"
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["m"]
