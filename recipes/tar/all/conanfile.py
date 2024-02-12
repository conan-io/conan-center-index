import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class TarConan(ConanFile):
    name = "tar"
    description = "GNU Tar provides the ability to create tar archives, as well as various other kinds of manipulation."
    license = "GPL-3-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/tar/"
    topics = "archive"

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def requirements(self):
        self.requires("bzip2/1.0.8", run=True, headers=False, libs=False)
        self.requires("lzip/1.23", run=True, headers=False, libs=False)
        self.requires("xz_utils/5.4.4", run=True, headers=False, libs=False)
        self.requires("zstd/1.5.5", run=True, headers=False, libs=False)
        # self.requires("lzo/2.10", run=True, headers=False, libs=False)

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("This recipe does not support Windows builds of tar")  # FIXME: fails on MSVC and mingw-w64
        if not self.dependencies["bzip2"].options.build_executable:
            raise ConanInvalidConfiguration("bzip2:build_executable must be enabled")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        tc.generate()
        tc.configure_args += [
            "--disable-acl",
            "--disable-nls",
            "--disable-rpath",
            "--without-posix-acls",
            "--without-selinux",
            "--with-gzip=gzip",  # FIXME: this will use system gzip
            "--with-bzip2=bzip2",
            "--with-lzip=lzip",
            "--with-lzma=lzma",
            "--without-lzop", # FIXME: lzo package does not build an executable
            "--with-xz=xz",
            "--with-zstd=zstd",
        ]
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            replace_in_file(
                self,
                os.path.join(self.source_folder, "gnu", "faccessat.c"),
                "_GL_INCLUDING_UNISTD_H",
                "_GL_INCLUDING_UNISTD_H_NOP",
            )

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "libexec"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        tar_bin = os.path.join(self.package_folder, "bin", "tar")
        self.conf_info.define("user.tar:path", tar_bin)
        self.env_info.TAR = tar_bin

        # TODO: to remove in conan v2
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
        self.user_info.tar = tar_bin
