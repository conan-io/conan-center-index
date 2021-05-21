from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibSafeCConan(ConanFile):
    name = "libsafec"
    description = "This library implements the secure C11 Annex K[^5] functions" \
            " on top of most libc implementations, which are missing from them."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rurban/safeclib"
    license = "MIT"
    topics = ("conan", "safec", "libc")

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = "patches/*"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _supported_compiler(self):
        compiler = self.settings.compiler
        version = tools.Version(self.settings.compiler.version)
        if compiler == "Visual Studio":
            return False
        if compiler == "gcc" and version < "5":
            return False
        return True

    def configure(self):
        if not self._supported_compiler:
            raise ConanInvalidConfiguration(
                "libsafec doesn't support {}/{}".format(
                    self.settings.compiler, self.settings.compiler.version))
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.options.shared:
            args = ["--enable-shared", "--disable-static"]
        else:
            args = ["--disable-shared", "--enable-static"]
        args.extend(["--disable-doc", "--disable-Werror"])
        if self.settings.build_type in ("Debug", "RelWithDebInfo"):
            args.append("--enable-debug")
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")),
                     win_bash=tools.os_info.is_windows, run_environment=True)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "libsafec"))
        self.cpp_info.libs = ["safec-{}".format(self.version)]
        self.cpp_info.names["pkg_config"] = "libsafec"

        bin_dir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_dir))
        self.env_info.PATH.append(bin_dir)
