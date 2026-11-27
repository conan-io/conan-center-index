import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=2.4"


class Lbzip2Conan(ConanFile):
    name = "lbzip2"
    package_type = "application"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kjn/lbzip2"
    license = "GPL-3.0-or-later"
    description = "A parallel, SMP-based, bzip2-compatible compression utility"
    topics = ("bzip2", "compression", "parallel")

    settings = "os", "arch", "compiler", "build_type"
    options = {"install_symlinks": [True, False]}
    default_options = {"install_symlinks": False}

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("lbzip2 requires a Unix-style operating system with pthreads")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Backport gnulib's glibc 2.28 detection fix (74d9d6a293d7).
        replace_in_file(self, os.path.join(self.source_folder, "lib", "fseterr.c"),
                        "defined _IO_ftrylockfile", "defined _IO_EOF_SEEN || defined _IO_ftrylockfile")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install(target="install-exec")
        if self.options.install_symlinks:
            bindir = os.path.join(self.package_folder, "bin")
            for name in ("bzip2", "bunzip2", "bzcat"):
                os.symlink("lbzip2", os.path.join(bindir, name))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.runenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))
