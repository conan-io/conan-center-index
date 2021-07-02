from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os


class IslConan(ConanFile):
    name = "isl"
    description = "isl is a library for manipulating sets and relations of integer points bounded by linear constraints."
    topics = ("conan", "isl", "integer", "set", "library")
    license = "MIT"
    homepage = "http://isl.gforge.inria.fr/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_int": ["gmp", "imath", "imath-32"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_int": "gmp",
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Cannot build shared isl library on Windows (due to libtool refusing to link to static/import libraries)")

    def requirements(self):
        if self.options.with_int == "gmp":
            self.requires("gmp/6.2.1")
        else:
            # FIXME: missing imath recipe
            raise ConanInvalidConfiguration("imath is not (yet) available on cci")

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20200517")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                    "CC": "{} cl -nologo -{}".format(tools.unix_path(self.deps_user_info["automake"].compile), self.settings.compiler.runtime),
                    "CXX": "{} cl -nologo -{}".format(tools.unix_path(self.deps_user_info["automake"].compile), self.settings.compiler.runtime),
                    "NM": "dumpbin -symbols",
                    "OBJDUMP": ":",
                    "RANLIB": ":",
                    "STRIP": ":",
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
        conf_args = [
            "--with-int={}".format(self.options.with_int),
            "--enable-portable-binary",
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        if self.options.with_int == "gmp":
            conf_args.extend([
                "--with-gmp=system",
                "--with-gmp-prefix={}".format(self.deps_cpp_info["gmp"].rootpath.replace("\\", "/")),
            ])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        os.unlink(os.path.join(os.path.join(self.package_folder, "lib", "libisl.la")))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "isl"
        self.cpp_info.libs = ["isl"]
