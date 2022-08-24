from conan import ConanFile, tools
from conans import AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LdnsConan(ConanFile):
    name = "ldns"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.nlnetlabs.nl/projects/ldns"
    description = "LDNS is a DNS library that facilitates DNS tool programming"
    topics = ("dns")

    settings = "os", "compiler", "build_type", "arch"
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

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows is not supported by the ldns recipe. Contributions are welcome.")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires("openssl/1.1.1o")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        def yes_no(v): return "yes" if v else "no"
        args = [
            # libraries
            f"--enable-shared={yes_no(self.options.shared)}",
            f"--enable-static={yes_no(not self.options.shared)}",
            f"--with-pic={yes_no(self.settings.os != 'Windows' and (self.options.shared or self.options.fPIC))}",
            "--disable-rpath",
            # dependencies
            f"--with-ssl={self.deps_cpp_info['openssl'].rootpath}",
            # DNSSEC algorithm support
            "--enable-ecdsa",
            "--enable-ed25519",
            "--enable-ed448",
            "--disable-dsa",
            "--disable-gost",
            "--enable-full-dane",
            # tooling
            "--disable-ldns-config",
            "--without-drill",
            "--without-examples",
            # library bindings
            "--without-pyldns",
            "--without-p5-dns-ldns",
        ]
        if self.settings.compiler == "apple-clang":
            args.append(f"--with-xcode-sdk={tools.XCRun(self.settings).sdk_version}")

        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)

        # This fixes the issue of linking against ldns in combination of openssl:shared=False, ldns:shared=True, and an older GCC:
        # > hidden symbol `pthread_atfork' in /usr/lib/x86_64-linux-gnu/libpthread_nonshared.a(pthread_atfork.oS) is referenced by DSO
        # OpenSSL adds -lpthread to link POSIX thread library explicitly. That is not correct because using the library
        # may require setting various on compilation as well. The compiler has a dedicated -pthread option for that.
        if self.settings.os == "Linux":
            self._autotools.libs.remove("pthread")
            env = self._autotools.vars
            env["CFLAGS"] += " -pthread"
        else:
            env = None

        self._autotools.configure(configure_dir=self._source_subfolder, args=args, vars=env)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        autotools = self._configure_autotools()
        for target in ["install-h", "install-lib"]:
            autotools.make(target=target)
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["ldns"]
