from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import contextlib
import os

required_conan_version = ">=1.33.0"


class LibstropheConan(ConanFile):
    name = "libstrophe"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/strophe/libstrophe"
    license = ("GPL-3.0", "MIT")
    description = "libstrophe is a lightweight XMPP client library written in C"
    topics = ("XMPP", "libstrophe", "jabber")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_tls": [True, False],
        "with_gnutls": [True, False],
        "with_schannel": [True, False],
        "enable_cares": [True, False],
        "xml_parser": ["libxml2", "libexpat"],
        "disable_getrandom": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_tls": False,
        "with_gnutls": False,
        "with_schannel": False,
        "enable_cares": False,
        "xml_parser": "libexpat",
        "disable_getrandom": True,
    }
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "cl -nologo",
                    "AR": "lib",
                    "LD": "link -nologo",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("gettext/0.21")
        self.build_requires("libtool/2.4.6")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def requirements(self):
        if self.options.xml_parser == "libxml2":
            self.requires("libxml2/2.9.14")
        else:
            self.requires("expat/2.4.8")
        if self.options.enable_cares:
            self.requires("c-ares/1.18.1")
        if not self.options.disable_tls:
            if self.options.with_schannel:
                if not self._settings_build.os == "Windows":
                    raise ConanInvalidConfiguration(
                        "libstrophe with schannel is only supported on Windows")
            elif self.options.with_gnutls:
                raise ConanInvalidConfiguration(
                    "libstrophe with gnutls not supported yet in this recipe")
            else:
                self.requires("openssl/1.1.1q")

    def validate(self):
        if self.options.with_gnutls:
            raise ConanInvalidConfiguration(
                "xmlsec with gnutls not supported yet in this recice")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(
            self, win_bash=self._settings_build.os == "Windows")
        self._autotools.libs = []
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) >= "12":
            self._autotools.flags.append("-FS")

        def yes_no(v): return "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--disable-examples",
        ]

        if not self.options.disable_tls:
            if self.options.with_schannel:
                if self._settings_build.os == "Windows":
                    args.append("--with-schannel")
                else:
                    raise ConanInvalidConfiguration(
                        "libstrophe with schannel is only supported on Windows")
            elif self.options.with_gnutls:
                raise ConanInvalidConfiguration(
                    "libstrophe with gnutls not supported yet in this recipe")
        else:
            args.append("--disable-tls")
        if self.options.enable_cares:
            args.append("--enable-cares")
        if self.options.disable_getrandom:
            args.append("--disable-getrandom")
        if self.options.xml_parser == "libxml2":
            args.append("--with-libmxl2")

        self._autotools.configure(
            args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            tools.rename(os.path.join(self.package_folder, "lib", "strophe.dll.lib"),
                         os.path.join(self.package_folder, "lib", "strophe.lib"))
        tools.remove_files_by_mask(self.package_folder, "*.la")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        if self.settings.os in ("FreeBSD", "Linux", "Macos"):
            self.cpp_info.system_libs = ["m", "resolv"]

        self.cpp_info.names["pkg_config"] = "libstrophe"
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "libstrophe")
        self.cpp_info.set_property(
            "cmake_target_name", "libstrophe::libstrophe")

        self.cpp_info.names["cmake_find_package"] = "libstrophe"
        self.cpp_info.names["cmake_find_package_multi"] = "libstrophe"

        self.cpp_info.libs = ["strophe"]

        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment var: {}".format(binpath))
        self.env_info.path.append(binpath)
