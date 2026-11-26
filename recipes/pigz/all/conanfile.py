import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import chdir, copy, get
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=2.4"


class PigzConan(ConanFile):
    name = "pigz"
    package_type = "application"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://zlib.net/pigz/"
    license = "Zlib", "Apache-2.0"
    description = "A parallel implementation of gzip for modern multi-processor, multi-core machines"
    topics = ("gzip", "compression", "parallel")

    settings = "os", "arch", "compiler", "build_type"
    options = {"install_symlinks": [True, False]}
    default_options = {"install_symlinks": False}

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("pigz requires a Unix-style operating system with pthreads")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        compiler = "clang" if self.settings.compiler in ("clang", "apple-clang") else "gcc"
        # Upstream's Makefile overrides environment flags unless passed as make arguments.
        args = [
            f'CC="${{CC:-{compiler}}}"',
            'CFLAGS="$CFLAGS $CPPFLAGS"',
            'LDFLAGS="$LDFLAGS"',
            'LIBS="$LIBS -lm -lpthread"',
        ]
        with chdir(self, self.source_folder):
            Autotools(self).make(args=args)

    def package(self):
        copy(self, "README", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYING", src=os.path.join(self.source_folder, "zopfli"),
             dst=os.path.join(self.package_folder, "licenses", "zopfli"))
        bindir = os.path.join(self.package_folder, "bin")
        copy(self, "pigz", src=self.source_folder, dst=bindir)
        aliases = ["unpigz"]
        if self.options.install_symlinks:
            aliases.extend(["gzip", "gunzip", "zcat"])
        for name in aliases:
            os.symlink("pigz", os.path.join(bindir, name))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.runenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))
