import glob
import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


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

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration(
                "libsafec doesn't support compiler: {} on OS: {}.".format(
                    self.settings.compiler, self.settings.os))
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
        if self.__autotools:
            return self.__autotools
        self.run("autoreconf -fiv", run_environment=True)
        self.__autotools = AutoToolsBuildEnvironment(self)
        if self.options.shared:
            args = ["--enable-shared", "--disable-static"]
        else:
            args = ["--disable-shared", "--enable-static"]
        args.extend(["--disable-doc", "--disable-dependency-tracking"])
        if self.settings.build_type in ("Debug", "RelWithDebInfo"):
            args.append("--enable-debug")
        self.__autotools.configure(args=args)
        return self.__autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Makefile.am"), "_@SAFEC_API_VERSION@", "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Makefile.am"), "-@SAFEC_API_VERSION@", "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "tests", "Makefile.am"), "-@SAFEC_API_VERSION@", "")
        with tools.chdir(self._source_subfolder):
            self._autotools.make()

    def package(self):
        with tools.chdir(self._source_subfolder):
            self._autotools.install()
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with tools.chdir(os.path.join(self.package_folder, "lib")):
            tools.rmdir("pkgconfig")
            tools.remove_files_by_mask(".", "*.la")

    def package_info(self):
        self.cpp_info.libs = ["safec"]
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
