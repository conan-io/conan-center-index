from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.files import get, rmdir, copy, replace_in_file, rm
from conan.errors import ConanInvalidConfiguration
import os


class Libpfm4Conan(ConanFile):
    name = "libpfm4"
    license = "MIT"
    homepage = "http://perfmon2.sourceforge.net"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A helper library to program the performance monitoring events"
    topics = ("perf", "pmu", "benchmark", "microbenchmark")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    package_type = "library"

    def validate(self):
        # The library doesn't really make much sense without perf_events API
        # and currently does not compile on modern Mac OS X && Windows
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("This library is Linux only")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def _patch_sources(self):
        if self.options.get_safe("fPIC"):
            # honor fPIC option
            replace_in_file(self, os.path.join(self.source_folder, "rules.mk"), "-fPIC", "")
            replace_in_file(self, os.path.join(self.source_folder, "rules.mk"), "-DPIC", "")

    def _yes_no(self, option):
        return "y" if option else "n"

    def build(self):
        self._patch_sources()
        args = [
            'DBG=',
            f'CONFIG_PFMLIB_SHARED={self._yes_no(self.options.shared)}',
            f'-C {self.source_folder}'
        ]
        autotools = Autotools(self)
        autotools.make(args=args)

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "err.h", dst=os.path.join(self.package_folder, "include", "perfmon"), src=os.path.join(self.source_folder, "include", "perfmon"))

        autotools = Autotools(self)
        autotools.install(args=[
            'DBG=',
            'LDCONFIG=true',
            f'CONFIG_PFMLIB_SHARED={self._yes_no(self.options.shared)}',
            f'DESTDIR={self.package_folder}{os.sep}',
            f'INCDIR=include{os.sep}',
            f'LIBDIR=lib{os.sep}',
            f'-C {self.source_folder}'
        ])
        rmdir(self, os.path.join(self.package_folder, "usr"))
        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["pfm"]
        # This currently only compiles on Linux, so always add the libs
        self.cpp_info.system_libs = ["pthread", "m"]

