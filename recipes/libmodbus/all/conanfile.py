from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import os

required_conan_version = ">=1.33.0"


class LibmodbusConan(ConanFile):
    name = "libmodbus"
    description = "libmodbus is a free software library to send/receive data according to the Modbus protocol"
    homepage = "https://libmodbus.org/"
    topics = ("conan", "libmodbus", "modbus", "protocol", "industry", "automation")
    license = "LGPL-2.1"
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

    @property
    def _settings_build(self):
        return self.settings_build if hasattr(self, "settings_build") else self.settings

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.3")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--disable-tests",
            "--without-documentation",
            "--prefix={}".format(tools.microsoft.unix_path(self, self.package_folder)),
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--enable-static", "--disable-shared"])
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) >= "12":
            if self.settings.build_type in ("Debug", "RelWithDebInfo"):
                self._autotools.flags.append("-FS")
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                    "LD": "link -nologo",
                    "AR": "{} \"lib -nologo -verbose\"".format(tools.microsoft.unix_path(self, self.deps_user_info["automake"].ar_lib)),
                    "RANLIB": ":",
                    "STRING": ":",
                    "NM": "dumpbin -symbols"}
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        if not self.options.shared:
            for decl in ("__declspec(dllexport)", "__declspec(dllimport)"):
                tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "src", "modbus.h"), decl, "")

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libmodbus.la"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            tools.files.rename(self, os.path.join(self.package_folder, "lib", "modbus.dll.lib"),
                         os.path.join(self.package_folder, "lib", "modbus.lib"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libmodbus"
        self.cpp_info.includedirs.append(os.path.join("include", "modbus"))
        self.cpp_info.libs = ["modbus"]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.system_libs = ["wsock32"]
