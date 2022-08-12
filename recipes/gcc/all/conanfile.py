import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.files import get, replace_in_file, rmdir, rm, copy
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout

required_conan_version = '>=1.49.0'


class GccConan(ConanFile):
    name = 'gcc'
    description = 'The GNU Compiler Collection includes front ends for C, ' \
                  'C++, Objective-C, Fortran, Ada, Go, and D, as well as ' \
                  'libraries for these languages (libstdc++,...). '
    topics = 'gcc', 'gnu', 'compiler', 'c', 'c++'
    homepage = 'https://gcc.gnu.org'
    url = 'https://github.com/conan-io/conan-center-index'
    license = 'GPL-3.0-only'
    settings = 'os', 'compiler', 'arch', 'build_type'
    requires = 'mpc/1.2.0', 'mpfr/4.1.0', 'gmp/6.2.1', 'zlib/1.2.12', 'isl/0.24'
    tool_requires = 'flex/2.6.4'
    short_paths = True

    _auto_tools = None

    def layout(self):
        basic_layout(self, src_folder=f'gcc-{self.version}')

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            '--enable-languages=c,c++',
            '--disable-nls',
            '--disable-multilib',
            '--disable-bootstrap',
            f'--prefix={self.package_folder}',
            '--libexecdir=$prefix/bin/libexec'
            f'--with-zlib={self.deps_cpp_info["zlib"].rootpath}',
            f'--with-gmp={self.deps_cpp_info["gmp"].rootpath}',
            f'--with-mpc={self.deps_cpp_info["mpc"].rootpath}',
            f'--with-mpfr={self.deps_cpp_info["mpfr"].rootpath}',
            f'--with-isl={self.deps_cpp_info["isl"].rootpath}',
            f'--with-pkgversion=\'conan GCC {self.version}\'',
            f'--program-suffix=-{self.version}',
            f'--with-bugurl={self.url}/issues'])
        if self.settings.os == 'Macos':
            tc.make_args.extend(['BOOT_LDFLAGS=-Wl,-headerpad_max_install_names'])
            tc.configure_args.append('--with-native-system-header-dir=/usr/include')
        tc.generate()

    def validate(self):
        if self.settings.os == 'Windows':
            raise ConanInvalidConfiguration('Windows is not yet supported. Contributions are welcome')
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("Apple silicon is not yet supported. Contributions are welcome")
        if cross_building(self):
            raise ConanInvalidConfiguration('no cross-building support (yet), sorry')

    def source(self):
        get(self, **self.conan_data['sources'][self.version], strip_root=True)

    @property
    def auto_tools(self):
        if self._auto_tools is not None:
            return self._auto_tools
        self._auto_tools = Autotools(self)
        return self._auto_tools

    def build(self):
        # If building on x86_64, change the default directory name for 64-bit libraries to "lib":
        replace_in_file(self, os.path.join(self.source_folder, "gcc", "config", "i386", "t-linux64"),
                        "m64=../lib64", "m64=../lib", strict=False)
        # Ensure correct install names when linking against libgcc_s;
        # see discussion in https://github.com/Homebrew/legacy-homebrew/pull/34303
        replace_in_file(self,
                        os.path.join(self.source_folder, 'libgcc', 'config', 't-slibgcc-darwin'),
                        '@shlib_slibdir@',
                        os.path.join(self.package_folder, 'lib'),
                        strict=False)
        self.auto_tools.configure()
        self.auto_tools.make()

    def package_id(self):
        del self.info.settings.compiler

    def package(self):
        if self.settings.build_type == 'Debug':
            self.auto_tools.install()
        else:
            self.auto_tools.make('install-strip')
        rmdir(self, os.path.join(self.package_folder, 'share'))
        rm(self, '*.la', self.package_folder, recursive=True)
        copy(self, pattern='COPYING*', dst=os.path.join(self.package_folder, "licenses"), src=self.folders.source)

    def package_info(self):
        bindir = os.path.join(self.package_folder, 'bin')
        self.output.info('Appending PATH env var with : ' + bindir)
        self.env_info.PATH = [bindir] + self.env_info.PATH

        cc = os.path.join(bindir, f'gcc-{self.version}')
        self.output.info('Creating CC env var with : ' + cc)
        self.env_info.CC = cc

        cxx = os.path.join(bindir, f'g++-{self.version}')
        self.output.info('Creating CXX env var with : ' + cxx)
        self.env_info.CXX = cxx

        if self.settings.os in ['Linux', 'FreeBSD']:
            self.cpp_info.system_libs = ['pthread', 'rt', 'dl', 'm']
