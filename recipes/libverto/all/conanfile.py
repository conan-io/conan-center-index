from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import contextlib
import os


required_conan_version = ">=1.33.0"


class LibVertoConan(ConanFile):
    name = "libverto"
    description = "An async event loop abstraction library."
    homepage = "https://github.com/latchset/libverto"
    topics = ("libverto", "async", "eventloop")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "pthread": [True, False],
        "with_glib": ["builtin", "external", False],
        "with_libev": ["builtin", "external", False],
        "with_libevent": ["builtin", "external", False],
        "with_tevent": ["external", False],  # tevent cannot be a builtin backend
        "default": ["glib", "libev", "libevent", "tevent"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "pthread": True,
        "with_glib": False,
        "with_libev": False,
        "with_libevent": "builtin",
        "with_tevent": False,
        "default": "libevent",
    }
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "patches/*"
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _backend_dict(self):
        return {
            "glib": self.options.with_glib,
            "libev": self.options.with_libev,
            "libevent": self.options.with_libevent,
            "tevent": self.options.with_tevent,
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.pthread

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("libverto does not support Visual Studio")
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Shared libraries are not supported on Windows")

        if not self._backend_dict[str(self.options.default)]:
            raise ConanInvalidConfiguration("Default backend({}) must be available".format(self.options.default))

        count = lambda iterable: sum(1 if it else 0 for it in iterable)
        count_builtins = count(str(opt) == "builtin" for opt in self._backend_dict.values())
        count_externals = count(str(opt) == "external" for opt in self._backend_dict.values())
        if count_builtins > 1:
            raise ConanInvalidConfiguration("Cannot have more then one builtin backend")
        if not self.options.shared:
            if count_externals > 0:
                raise ConanInvalidConfiguration("Cannot have an external backend when building a static libverto")
        if count_builtins > 0 and count_externals > 0:
            raise ConanInvalidConfiguration("Cannot combine builtin and external backends")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def requirements(self):
        if self.options.with_glib:
            self.requires("glib/2.69.2")
        if self.options.with_libevent:
            self.requires("libevent/2.1.12")
        if self.options.with_libev:
            self.requires("libev/4.33")
        if self.options.with_tevent:
            # FIXME: missing tevent recipe
            raise ConanInvalidConfiguration("tevent is not (yet) available on conan-center")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")
        self.build_requires("libtool/2.4.6")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "{} cl -nologo".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].compile)),
                    "LD": "{} link -nologo".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].compile)),
                    "AR": "{} lib".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].ar_lib)),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        yes_no_builtin = lambda v: {"external": "yes", "False": "no", "builtin": "builtin"}[str(v)]
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-pthread={}".format(yes_no(self.options.get_safe("pthread", False))),
            "--with-glib={}".format(yes_no_builtin(self.options.with_glib)),
            "--with-libev={}".format(yes_no_builtin(self.options.with_libev)),
            "--with-libevent={}".format(yes_no_builtin(self.options.with_libevent)),
            "--with-tevent={}".format(yes_no_builtin(self.options.with_tevent)),
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        with tools.files.chdir(self, self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True, win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        tools.files.rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_id(self):
        del self.info.options.default

    def package_info(self):
        self.cpp_info.components["verto"].libs = ["verto"]
        self.cpp_info.components["verto"].names["pkg_config"] = "libverto"
        if self.settings.os == "Linux":
            self.cpp_info.components["verto"].system_libs.append("dl")
            if self.options.pthread:
                self.cpp_info.components["verto"].system_libs.append("pthread")

        if self.options.with_glib == "builtin":
            self.cpp_info.components["verto"].requires.append("glib::glib")
        elif self.options.with_glib:
            self.cpp_info.components["verto-glib"].libs = ["verto-glib"]
            self.cpp_info.components["verto-glib"].names["pkg_config"] = "libverto-glib"
            self.cpp_info.components["verto-glib"].requires = ["verto", "glib::glib"]

        if self.options.with_libev == "builtin":
            self.cpp_info.components["verto"].requires.append("libev::libev")
        elif self.options.with_libev:
            self.cpp_info.components["verto-libev"].libs = ["verto-libev"]
            self.cpp_info.components["verto-libev"].names["pkg_config"] = "libverto-libev"
            self.cpp_info.components["verto-libev"].requires = ["verto", "libev::libev"]

        if self.options.with_libevent == "builtin":
            self.cpp_info.components["verto"].requires.append("libevent::libevent")
        elif self.options.with_libevent:
            self.cpp_info.components["verto-libevent"].libs = ["verto-libevent"]
            self.cpp_info.components["verto-libevent"].names["pkg_config"] = "libverto-libevent"
            self.cpp_info.components["verto-libevent"].requires = ["verto", "libevent::libevent"]

        if self.options.with_tevent:
            self.cpp_info.components["verto-tevent"].libs = ["verto-tevent"]
            self.cpp_info.components["verto-tevent"].names["pkg_config"] = "libverto-tevent"
            self.cpp_info.components["verto-tevent"].requires = ["verto", "tevent::tevent"]

        self.user_info.backends = ",".join(tuple(backend for backend, opt in self._backend_dict.items() if opt != False))
