from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.files import get, rmdir, copy, replace_in_file
import os


class Libpfm4Conan(ConanFile):
    name = "libpfm4"
    license = "MIT"
    homepage = "https://github.com/wcohen/libpfm4"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("A helper library to program the performance monitoring events")
    topics = ("perf", "pmu", "benchmark", "microbenchmark")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def _patch_sources(self):
        if not self.options.shared:
            # honor fPIC option
            replace_in_file(self, os.path.join(self.source_folder, "rules.mk"), "-fPIC", "")
            replace_in_file(self, os.path.join(self.source_folder, "rules.mk"), "-DPIC", "")

    def build(self):
        self._patch_sources()
        args = [
            'DBG=',
            'CONFIG_PFMLIB_SHARED={}'.format("y" if self.options.shared else "n"),
            f'-C {self.source_folder}'
        ]
        autotools = Autotools(self)
        autotools.make(args=args)

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        args = [
            'DBG=',
            'LDCONFIG=true',
            'CONFIG_PFMLIB_SHARED={}'.format("y" if self.options.shared else "n"),
            f'DESTDIR={self.package_folder}{os.sep}',
            f'INCDIR=include{os.sep}',
            f'LIBDIR=lib{os.sep}',
            f'-C {self.source_folder}'
        ]
        # due to bug, Mac install phase fails with config shared
        if self.settings.os == 'Macos':
            args.append('CONFIG_PFMLIB_SHARED=n')

        copy(self, "err.h", dst=os.path.join(self.package_folder, "include", "perfmon"), src=os.path.join(self.source_folder, "include", "perfmon"))
        autotools = Autotools(self)
        autotools.install(args=args)
        rmdir(self, os.path.join(self.package_folder, "usr"))

    def package_info(self):
        self.cpp_info.libs = ["pfm"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread", "m"]
