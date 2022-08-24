from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibRHashConan(ConanFile):
    name = "librhash"
    description = "Great utility for computing hash sums"
    topics = ("rhash", "hash", "checksum")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://rhash.sourceforge.net/"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
    }

    exports_sources = "patches/*"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("Visual Studio is not supported")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.compiler in ("apple-clang", ):
            if self.settings.arch in ("armv7", ):
                self._autotools.link_flags.append("-arch armv7")
            elif self.settings.arch in ("armv8", ):
                self._autotools.link_flags.append("-arch arm64")
        vars = self._autotools.vars
        conf_args = [
            # librhash's configure script does not understand `--enable-opt1=yes`
            "--enable-openssl" if self.options.with_openssl else "--disable-openssl",
            "--disable-gettext",
            # librhash's configure script is custom and does not understand "--bindir=${prefix}/bin" arguments
            "--prefix={}".format(tools.unix_path(self.package_folder)),
            "--bindir={}".format(tools.unix_path(os.path.join(self.package_folder, "bin"))),
            "--libdir={}".format(tools.unix_path(os.path.join(self.package_folder, "lib"))),
            # the configure script does not use CPPFLAGS, so add it to CFLAGS/CXXFLAGS
            "--extra-cflags={}".format("{} {}".format(vars["CFLAGS"], vars["CPPFLAGS"])),
            "--extra-ldflags={}".format(vars["LDFLAGS"]),
        ]
        if self.options.shared:
            conf_args.extend(["--enable-lib-shared", "--disable-lib-static"])
        else:
            conf_args.extend(["--disable-lib-shared", "--enable-lib-static"])

        with tools.environment_append({
            "BUILD_TARGET": tools.get_gnu_triplet(str(self.settings.os), str(self.settings.arch), str(self.settings.compiler)),
        }):
            self._autotools.configure(args=conf_args, use_default_install_dirs=False, build=False, host=False)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        with tools.files.chdir(self, self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with tools.files.chdir(self, self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
            autotools.make(target="install-lib-headers")
            with tools.files.chdir(self, "librhash"):
                if self.options.shared:
                    autotools.make(target="install-so-link")
        tools.files.rmdir(self, os.path.join(self.package_folder, "bin"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "etc"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "LibRHash"
        self.cpp_info.names["cmake_find_package_multi"] = "LibRHash"
        self.cpp_info.names["pkg_config"] = "librhash"
        self.cpp_info.libs = ["rhash"]
