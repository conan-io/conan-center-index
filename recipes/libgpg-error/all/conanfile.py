from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
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
    options = {"shared": [True, False]}
    default_options = {"shared": False}

    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux is supported")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        # the previous step might hang when converting from ISO-8859-2 to UTF-8 late in the build process
        # os.unlink(os.path.join(self._source_subfolder, "po", "ro.po"))
        build = None
        host = None
        rc = None
        env = dict()
        args = ["--disable-dependency-tracking",
                "--disable-nls",
                "--disable-languages",
                "--disable-doc",
                "--disable-tests"]
        if self.options.shared:
            args.append("--with-pic")
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])
        if self.settings.os == "Linux" and self.settings.arch == "x86":
            host = "i686-linux-gnu"

        with tools.chdir(self._source_subfolder):
            with tools.environment_append(env):
                env_build = AutoToolsBuildEnvironment(self)
                env_build.configure(args=args, build=build, host=host)
                env_build.make()
                env_build.install()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        la = os.path.join(self.package_folder, "lib", "libgpg-error.la")
        if os.path.isfile(la):
            os.unlink(la)
        shutil.rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))
        shutil.rmtree(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["gpg-error"]
