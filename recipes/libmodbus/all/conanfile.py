from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import os


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
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libmodbus-{}".format(self.version), self._source_subfolder)

    def build_requirements(self):
        if self.settings.compiler == "Visual Studio":
            self.build_requires("automake/1.16.1")
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ \
                and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--disable-tests",
            "--without-documentation",
            "--prefix={}".format(tools.unix_path(self.package_folder)),
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--enable-static", "--disable-shared"])
        if self.settings.compiler == "Visual Studio":
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
                    "AR": "{} \"lib -nologo -verbose\"".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                    "RANLIB": ":",
                    "STRING": ":",
                    "NM": "dumpbin -symbols"}
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _patch_sources(self):
        for patchdata in self.conan_data["patches"][self.version]:
            tools.patch(**patchdata)
        if not self.options.shared:
            for decl in ("__declspec(dllexport)", "__declspec(dllimport)"):
                tools.replace_in_file(os.path.join(self._source_subfolder, "src", "modbus.h"), decl, "")

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
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "modbus"))
        lib = "modbus"
        if self.settings.os == "Windows" and self.options.shared:
            lib += ".dll" + (".lib" if self.settings.compiler == "Visual Studio" else ".a")
        self.cpp_info.libs = [lib]
        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs = ["wsock32"]
