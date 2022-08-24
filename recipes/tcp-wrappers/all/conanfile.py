import os
from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration


class TcpWrappersConan(ConanFile):
    name = "tcp-wrappers"
    homepage = "ftp://ftp.porcupine.org/pub/security/index.html"
    description = "A security tool which acts as a wrapper for TCP daemons"
    topics = ("conan", "tcp", "ip", "daemon", "wrapper")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD"
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
    generators = "cmake"

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
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio is not supported")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("tcp_wrappers_{}-ipv6.4".format(self.version), self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.files.patch(self, **patch)

    def build(self):
        self._patch_sources()
        with tools.chdir(self._source_subfolder):
            autotools = AutoToolsBuildEnvironment(self)
            make_args = [
                "REAL_DAEMON_DIR={}".format(tools.unix_path(os.path.join(self.package_folder, "bin"))),
                "-j1",
                "SHEXT={}".format(self._shext),
            ]
            if self.options.shared:
                make_args.append("shared=1")
            env_vars = autotools.vars
            if self.options.get_safe("fPIC", True):
                env_vars["CFLAGS"] += " -fPIC"
            env_vars["ENV_CFLAGS"] = env_vars["CFLAGS"]
            # env_vars["SHEXT"] = self._shext
            print(env_vars)
            with tools.environment_append(env_vars):
                autotools.make(target="linux", args=make_args)

    @property
    def _shext(self):
        if tools.is_apple_os(self.settings.os):
            return ".dylib"
        return ".so"

    def package(self):
        self.copy(pattern="DISCLAIMER", src=self._source_subfolder, dst="licenses")

        for exe in ("safe_finger", "tcpd", "tcpdchk", "tcpdmatch", "try-from"):
            self.copy(exe, src=self._source_subfolder, dst="bin", keep_path=False)
        self.copy("tcpd.h", src=self._source_subfolder, dst="include", keep_path=False)
        if self.options.shared:
            self.copy("libwrap{}".format(self._shext), src=self._source_subfolder, dst="lib", keep_path=False)
        else:
            self.copy("libwrap.a", src=self._source_subfolder, dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["wrap"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
