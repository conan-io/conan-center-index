import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import shutil

required_conan_version = ">=1.33.0"

class GPGErrorConan(ConanFile):
    name = "libgpg-error"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gnupg.org/software/libgpg-error/index.html"
    topics = ("conan", "gpg", "gnupg")
    description = "Libgpg-error is a small library that originally defined common error values for all GnuPG " \
                  "components."
    license = "GPL-2.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": False
    }

    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("This recipe only support Linux. You can contribute Windows and/or Macos support.")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure(self):
        build = None
        host = None
        args = ["--disable-dependency-tracking",
                "--disable-nls",
                "--disable-languages",
                "--disable-doc",
                "--disable-tests"]
        if 'fPIC' in self.options and self.options.fPIC:
            args.append("--with-pic")
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])
        if self.settings.os == "Linux" and self.settings.arch == "x86":
            host = "i686-linux-gnu"

        env_build = AutoToolsBuildEnvironment(self)
        env_build.configure(args=args, build=build, host=host)

        return env_build

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        # the previous step might hang when converting from ISO-8859-2 to UTF-8 late in the build process
        # os.unlink(os.path.join(self._source_subfolder, "po", "ro.po"))
        with tools.chdir(self._source_subfolder):
            env_build = self._configure()
            env_build.make()

    def package(self):
        with tools.chdir(self._source_subfolder):
            env_build = self._configure()
            env_build.install()
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*la")
        shutil.rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))
        shutil.rmtree(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["gpg-error"]
        # FIXME: missing names for pkg_config generator
