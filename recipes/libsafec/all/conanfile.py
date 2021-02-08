import glob
import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.29.1"


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

    build_requires = "autoconf/2.69", "libtool/2.4.6"
    exports_sources = "patches/*"

    __autotools = None
    _source_subfolder = "source_subfolder"

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("safeclib-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _autotools(self):
        if self.__autotools is None:
            self.__autotools = AutoToolsBuildEnvironment(self)
        return self.__autotools

    def _autotools_configure(self):
        if self.options.shared:
            args = ["--enable-shared", "--disable-static"]
        else:
            args = ["--disable-shared", "--enable-static"]
        args.extend(["--disable-doc", "--disable-Werror"])
        if self.settings.build_type in ("Debug", "RelWithDebInfo"):
            args.append("--enable-debug")
        self._autotools.configure(args=args)

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("autoreconf -fiv", run_environment=True)
            self._autotools_configure()
            self._autotools.make()

    def package(self):
        with tools.chdir(self._source_subfolder):
            self._autotools.install()
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with tools.chdir(os.path.join(self.package_folder, "lib")):
            tools.rmdir("pkgconfig")
            tools.remove_files_by_mask(".", "*.la")

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "libsafec"))
        self.cpp_info.libs = ["safec-{}".format(self.version)]
        self.cpp_info.names["pkg_config"] = "libsafec"

        bin_dir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_dir))
        self.env_info.PATH.append(bin_dir)
