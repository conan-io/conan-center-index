from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class Pthreads4WConan(ConanFile):
    name = "pthreads4w"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/pthreads4w/"
    description = "POSIX Threads for Windows"
    license = "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
        "exception_scheme": ["CPP", "SEH", "default"]}
    default_options = {'shared': False, 'exception_scheme': 'default'}

    _source_folder = "source_folder"

    def configure(self):
        if self.settings.os != 'Windows':
            raise ConanInvalidConfiguration('pthreads4w can only target Windows')
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self.settings.compiler != 'Visual Studio':
            if "CONAN_BASH_PATH" not in os.environ and tools.os_info.detect_windows_subsystem() != 'msys2':
                self.build_requires('msys2/20190524')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        for f in os.listdir():
            if os.path.isdir(f) and f.startswith('pthreads'):
                os.rename(f, self._source_folder)

    def build(self):
        with tools.chdir(self._source_folder):
            if self.settings.compiler == "Visual Studio":
                tools.replace_in_file('Makefile',
                '	copy pthreadV*.lib $(LIBDEST)',
                '	if exist pthreadV*.lib copy pthreadV*.lib $(LIBDEST)')
                tools.replace_in_file('Makefile',
                '	copy libpthreadV*.lib $(LIBDEST)',
                '	if exist libpthreadV*.lib copy libpthreadV*.lib $(LIBDEST)')
                args = ['VCE' if self.options.exception_scheme == "CPP" \
                        else 'VSE' if self.options.exception_scheme == 'SEH'\
                        else 'VC']
                if not self.options.shared:
                    args[0] += '-static'
                if self.settings.build_type == 'Debug':
                    args[0] += '-debug'
                with tools.vcvars(self.settings):
                    self.run('nmake %s' % ' '.join(args))
            else:
                self.run('autoheader', win_bash=True)
                self.run('autoconf', win_bash=True)
                self.run('./configure', win_bash=True)
                args = ['GCE' if self.options.exception_scheme == "CPP" \
                        else 'GC']
                if not self.options.shared:
                    args[0] += '-static'
                if self.settings.build_type == 'Debug':
                    args[0] += '-debug'
                self.run('make %s' % ' '.join(args), win_bash=True)

    def package(self):
        with tools.chdir(self._source_folder):
            if self.settings.compiler == "Visual Studio":
                with tools.vcvars(self.settings):
                    self.run('nmake install DESTROOT=%s' % self.package_folder)
            else:
                self.run('make install prefix=%s' % tools.unix_path(self.package_folder))
        self.copy('LICENSE', dst='licenses', src=self._source_folder)


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["__PTW32_STATIC_LIB"]
        self.cpp_info.defines.append(
            '__PTW32_CLEANUP_CXX' if self.options.exception_scheme == "CPP" else\
            '__PTW32_CLEANUP_SEH' if self.options.exception_scheme == "SEH" else\
            '__PTW32_CLEANUP_C')
            

