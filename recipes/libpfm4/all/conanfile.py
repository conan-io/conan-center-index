from conan import ConanFile
from conan.tools.files import get, chdir, rmdir, collect_libs
import os


class Libpfm4Conan(ConanFile):
    name = "libpfm4"
    license = "MIT"
    homepage = "https://github.com/wcohen/libpfm4"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "a helper library to program the performance monitoring events")
    topics = ("perf", "pmu", "benchmark", "microbenchmark")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "src/*"

    def source(self):
        get(self,
                  **self.conan_data['sources'][self.version],
                  strip_root=True,
                  destination=self.source_folder)

    def config_options(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        with chdir(self, self.source_folder):
            self.run('make')

    def package(self):
        make_params = {
            'DESTDIR': self.package_folder + os.sep,
            'INCDIR': 'include' + os.sep,
            'LIBDIR': 'lib' + os.sep,
        }
        # due to bug, Mac install phase fails with config shared
        if self.settings.os == 'Macos':
            make_params['CONFIG_PFMLIB_SHARED'] = 'n'
        make_params_str = ' '.join('{}={}'.format(k, v)
                                   for k, v in make_params.items())
        self.copy("COPYING", dst="licenses", src=self.source_folder)
        self.copy("include/perfmon/err.h", dst=".", src=self.source_folder)
        with chdir(self, self.source_folder):
            self.run('make install {}'.format(make_params_str))
        rmdir(self, os.path.join(self.package_folder, "usr"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.includedirs = ["include"]
