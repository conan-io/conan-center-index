from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os


class LibTarConan(ConanFile):
    name = "libtar"
    description = "libtar is a library for manipulating tar files from within C programs."
    topics = ("conan", "libtar")
    license = "BSD-3-Clause"
    homepage = "https://repo.or.cz/libtar.git"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("libtar does not support Visual Studio")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("libtar-*")[0], self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        conf_args = [
            "--with-zlib" if self.options.with_zlib else "--without-zlib",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        if self.options.with_zlib:
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure.ac"),
                                  "AC_CHECK_LIB([z], [gzread])",
                                  "AC_CHECK_LIB([{}], [gzread])".format(self.deps_cpp_info["zlib"].libs[0]))

    def build(self):
        self._patch_sources()
        with tools.chdir(self._source_subfolder):
            self.run("autoreconf -fiv", run_environment=True, win_bash=tools.os_info.is_windows)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        os.unlink(os.path.join(os.path.join(self.package_folder, "lib", "libtar.la")))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["tar"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.deps_env_info.PATH.append(bin_path)
