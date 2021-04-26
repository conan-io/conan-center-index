from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import os


class Re2CConan(ConanFile):
    name = "re2c"
    description = "re2c is a free and open-source lexer generator for C, C++ and Go."
    topics = ("conan", "re2c", "lexer", "language", "tokenizer", "flex")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://re2c.org/"
    license = "Unlicense"
    settings = "os", "arch", "build_type", "compiler"
    exports_sources = "patches/**"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("re2c-{}".format(self.version), self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "CC": "{} -nologo".format(tools.unix_path(os.path.join(self.build_folder, "msvc_cl.sh"))),
                    "CXX": "{} -nologo".format(tools.unix_path(os.path.join(self.build_folder, "msvc_cl.sh"))),
                    "LD": "{} -nologo".format(tools.unix_path(os.path.join(self.build_folder, "msvc_cl.sh"))),
                    "CXXLD": "{} -nologo".format(tools.unix_path(os.path.join(self.build_folder, "msvc_cl.sh"))),
                    "AR": "lib",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
            self._autotools.cxx_flags.append("-EHsc")
        self._autotools.configure(configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make(args=["V=1"])

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)
        self.copy("NO_WARRANTY", src=self._source_subfolder, dst="licenses", keep_path=False)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
