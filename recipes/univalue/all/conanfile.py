from conans import ConanFile, tools, AutoToolsBuildEnvironment
from contextlib import contextmanager
import os

required_conan_version = ">=1.33.0"


class UnivalueConan(ConanFile):
    name = "univalue"
    description = "High performance RAII C++ JSON library and universal value object class"
    topics = "conan", "univalue", "universal", "json", "encoding", "decoding"
    license = "MIT"
    homepage = "https://github.com/jgarzik/univalue"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "patches/**"
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
        self.build_requires("libtool/2.4.6")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools =  AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        if self.settings.compiler == "Visual Studio":
            self._autotools.flags.append("-FS")
            self._autotools.cxx_flags.append("-EHsc")
        conf_args = []
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            tools.replace_in_file("libtool", "-Wl,-DLL,-IMPLIB", "-link -DLL -link -DLL -link -IMPLIB")
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                    "CPP": "cl -nologo -EP",
                    "LD": "link",
                    "CXXLD": "link",
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                    "NM": "dumpbin -symbols",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def build(self):
        self._patch_sources()
        with tools.chdir(self._source_subfolder):
            self.run("{} --verbose --install --force".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        suffix = ".dll" if self.options.shared and self.settings.os == "Windows" else ""
        if self.settings.compiler == "Visual Studio":
            suffix += ".lib"
        self.cpp_info.libs = ["univalue{}".format(suffix)]
        if self.options.shared:
            self.cpp_info.defines = ["UNIVALUE_SHARED"]

        self.cpp_info.names["pkg_config"] = "univalue"
