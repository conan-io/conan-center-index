from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class STXConan(ConanFile):
    name = 'stx'
    homepage = 'https://github.com/lamarrr/STX'
    license = 'MIT'
    url = 'https://github.com/conan-io/conan-center-index'
    description = 'C++17 & C++ 20 error-handling and utility extensions.'
    generators = 'cmake_find_package'
    topics = 'error-handling', 'result', 'option', 'backtrace', 'panic'
    settings = 'os', 'compiler', 'build_type', 'arch'
    options = {
        'backtrace': [True, False],
        'panic_backtrace': [True, False],
        'override_panic_handler': [True, False],
        'shared': [True, False],
        'fPIC': [True, False],
        'visible_panic_hook': [True, False],
    }
    default_options = {
        'backtrace': False,
        'override_panic_handler': False,
        'shared': False,
        'fPIC': True,
    }
    exports_sources = ['patches/*']

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.panic_backtrace == None:
            self.options.panic_backtrace = (
                self.options.backtrace and
                not self.options.override_panic_handler
            )

        if self.options.visible_panic_hook == None:
            self.options.visible_panic_hook = self.options.shared

        compiler = self.settings.compiler
        compiler_version = tools.Version(self.settings.compiler.version)
        standards = ['17', '20', 'gnu17', 'gnu20']

        if compiler.cppstd and not str(compiler.cppstd) in standards:
            raise ConanInvalidConfiguration('STX requires C++17 support')

        if compiler == 'Visual Studio' and compiler_version < 16:
            raise ConanInvalidConfiguration('STX requires C++17 support')

        if compiler in ['gcc', 'clang'] and compiler_version < 6:
            raise ConanInvalidConfiguration('STX requires C++17 support')

        if compiler == 'apple-clang':
            raise ConanInvalidConfiguration(
                'STX requires C++17 language and standard library features'
            )

        if (compiler == 'Visual Studio' and self.options.shared and
                tools.Version(self.version) <= '1.0.1'):
            raise ConanInvalidConfiguration(
                'shared library build does not work on windows with '
                'STX version <= 1.0.1')

    def requirements(self):
        if self.options.backtrace:
            self.requires('abseil/20200923.1')

    @property
    def _source_subfolder(self):
        return f'STX-{self.version}'

    def source(self):
        tools.get(**self.conan_data['sources'][self.version])

        if self.version in self.conan_data['patches']:
            for patch in self.conan_data['patches'][self.version]:
                tools.patch(base_path=self._source_subfolder, **patch)

    def build(self):
        cmake = CMake(self)
        cmake.definitions['STX_BUILD_SHARED'] = self.options.shared
        cmake.definitions['STX_ENABLE_BACKTRACE'] = self.options.backtrace
        cmake.definitions['STX_ENABLE_PANIC_BACKTRACE'] = \
            self.options.panic_backtrace
        cmake.definitions['STX_OVERRIDE_PANIC_HANDLER'] = \
            self.options.override_panic_handler
        cmake.definitions['STX_VISIBLE_PANIC_HOOK'] = \
            self.options.visible_panic_hook

        cmake.configure(source_dir=self._source_subfolder)
        cmake.build()

    def package(self):
        self.copy(
            '*.h',
            dst='include',
            src=os.path.join(self._source_subfolder, 'include')
        )

        self.copy('*.lib', dst='lib', keep_path=False)
        self.copy('*.dll', dst='bin', keep_path=False)
        self.copy('*.so', dst='lib', keep_path=False)
        self.copy('*.dylib', dst='lib', keep_path=False)
        self.copy('*.a', dst='lib', keep_path=False)

        self.copy('LICENSE', dst='licenses', src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.options.backtrace:
            self.cpp_info.requires = [
                'abseil::absl_stacktrace',
                'abseil::absl_symbolize'
            ]

        if self.options.visible_panic_hook:
            self.cpp_info.defines.append('STX_VISIBLE_PANIC_HOOK')

        if self.options.override_panic_handler:
            self.cpp_info.defines.append('STX_OVERRIDE_PANIC_HANDLER')

        if self.options.backtrace and not self.options.override_panic_handler:
            self.cpp_info.defines.append('STX_ENABLE_PANIC_BACKTRACE')
