from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import os


class XapianCoreConan(ConanFile):
    name = "xapian-core"
    description = "Xapian is a highly adaptable toolkit which allows developers to easily add advanced indexing and search facilities to their own applications."
    topics = ("conan", "xapian", "search", "engine", "indexing", "query")
    license = "GPL-v2"
    homepage = "https://xapian.org/"
    url = "https://github.com/conan-io/conan-center-index"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    @contextmanager
    def _build_context(self):
        env = {}
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env.update({
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                    "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "NM": "dumpbin -symbols",
                    "OBJDUMP": ":",
                    "RANLIB": ":",
                    "STRIP": ":",
                })
                with tools.environment_append(env):
                    yield
        else:
            with tools.environment_append(env):
                yield

    @property
    def _datarootdir(self):
        return os.path.join(self.package_folder, "bin", "share")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--datarootdir={}".format(self._datarootdir.replace("\\", "/")),
            "--disable-documentation",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        os.unlink(os.path.join(os.path.join(self.package_folder, "lib", "libxapian.la")))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self._datarootdir, "doc"))
        tools.rmdir(os.path.join(self._datarootdir, "man"))

    def package_info(self):
        self.cpp_info.libs = ["xapian"]
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["uuid", "rt"]

        self.cpp_info.names["cmake_find_package"] = "xapian"
        self.cpp_info.names["cmake_find_package_multi"] = "xapian"
        # FIXME: must define XAPIAN_INCLUDE_DIRS and XAPIAN_LIBRARIES cmake variables

        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(binpath))
        self.env_info.PATH.append(binpath)

        automake_path = os.path.join(self._datarootdir, "aclocal")
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment variable: {}".format(automake_path))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(tools.unix_path(automake_path))
