from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class TarConan(ConanFile):
    name = "tar"
    description = "GNU Tar provides the ability to create tar archives, as well as various other kinds of manipulation."
    topics = ("tar", "archive")
    license = "GPL-3-or-later"
    homepage = "https://www.gnu.org/software/tar/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("bzip2/1.0.8")
        self.requires("lzip/1.21")
        self.requires("xz_utils/5.2.5")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("This recipe does not support Windows builds of tar")  # FIXME: fails on MSVC and mingw-w64
        if not self.options["bzip2"].build_executable:
            raise ConanInvalidConfiguration("bzip2:build_executable must be enabled")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.libs = []
        bzip2_exe = "bzip2"  # FIXME: get from bzip2 recipe
        lzip_exe = "lzip"  # FIXME: get from lzip recipe
        lzma_exe = "lzma"  # FIXME: get from xz_utils recipe
        xz_exe = "xz"  # FIXME: get from xz_utils recipe
        args = [
            "--disable-acl",
            "--disable-nls",
            "--disable-rpath",
            # "--without-gzip",  # FIXME: this will use system gzip
            "--without-posix-acls",
            "--without-selinux",
            "--with-bzip2={}".format(bzip2_exe),
            "--with-lzip={}".format(lzip_exe),
            "--with-lzma={}".format(lzma_exe),
            # "--without-lzop",  # FIXME: this will use sytem lzop
            "--with-xz={}".format(xz_exe),
            # "--without-zstd",  # FIXME: this will use system zstd (current zstd recipe does not build programs)
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        if self.settings.compiler == "Visual Studio":
            tools.replace_in_file(os.path.join(self._source_subfolder, "gnu", "faccessat.c"),
                                  "_GL_INCLUDING_UNISTD_H", "_GL_INCLUDING_UNISTD_H_NOP")
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        tar_bin = os.path.join(self.package_folder, "bin", "tar")
        self.user_info.tar = tar_bin
        self.env_info.TAR = tar_bin
