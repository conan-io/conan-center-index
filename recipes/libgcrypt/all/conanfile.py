import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class LibgcryptConan(ConanFile):
    name = "libgcrypt"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnupg.org/download/index.html#libgcrypt"
    description = "Libgcrypt is a general purpose cryptographic library originally based on code from GnuPG"
    topics = ("libgcrypt", "gcrypt", "gnupg", "gpg", "crypto", "cryptography")
    license = "LGPL-2.1-or-later"
    settings = "os", "arch", "compiler", "build_type"
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

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("This recipe only support Linux. You can contribute Windows and/or Macos support.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def requirements(self):
        self.requires("libgpg-error/1.36")
        self.requires("libcap/2.50")

    def _configure(self):
        if self._autotools:
            return self._autotools
        args = ["--disable-doc"]
        args.append("--with-libgpg-error-prefix={}".format(self.deps_cpp_info["libgpg-error"].rootpath))
        if self.options.get_safe("fPIC", True):
            args.append("--with-pic")
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])

        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        env_build = self._configure()
        env_build.make()

    def package(self):
        env_build = self._configure()
        env_build.install()
        self.copy(pattern="COPYING*", dst="licenses", src=self._source_subfolder)
        tools.files.rm(self, "*la", os.path.join(self.package_folder, "lib"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["gcrypt"]
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.cpp_info.names["pkg_config"] = "gcrypt"
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
