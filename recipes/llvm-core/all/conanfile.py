from conans.errors import ConanInvalidConfiguration
from conans import ConanFile, CMake, tools

from pathlib import Path
import json
import re
import os


class LLVMCoreConan(ConanFile):
    name = 'llvm-core'
    description = (
        'A toolkit for the construction of highly optimized compilers,'
        'optimizers, and runtime environments.'
    )
    license = 'Apache-2.0 WITH LLVM-exception'
    topics = ('conan', 'llvm')
    homepage = 'https://github.com/llvm/llvm-project/tree/master/llvm'
    url = 'https://github.com/conan-io/conan-center-index'

    settings = ('os', 'arch', 'compiler', 'build_type')
    options = {
        'shared': [True, False],
        'fPIC': [True, False],
        'components': 'ANY',
        'targets': 'ANY',
        'exceptions': [True, False],
        'rtti': [True, False],
        'threads': [True, False],
        'lto': ['On', 'Off', 'Full', 'Thin'],
        'static_stdlib': [True, False],
        'unwind_tables': [True, False],
        'expensive_checks': [True, False],
        'use_perf': [True, False],
        'with_zlib': [True, False],
        'with_xml2': [True, False],
        'with_ffi': [True, False]
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'components': 'all',
        'targets': 'all',
        'exceptions': True,
        'rtti': True,
        'threads': True,
        'lto': 'Off',
        'static_stdlib': False,
        'unwind_tables': True,
        'expensive_checks': False,
        'use_perf': False,
        'with_zlib': True,
        'with_xml2': True,
        'with_ffi': False
    }

    exports_sources = ['CMakeLists.txt', 'patches/*']
    generators = 'cmake'
    no_copy_source = True

    _source_subfolder = 'source'

    def _configure_cmake(self):
        if self.settings.compiler == 'Visual Studio':
            generator = os.getenv('CONAN_CMAKE_GENERATOR', 'NMake Makefiles')
            cmake = CMake(self, generator=generator)
        else:
            cmake = CMake(self)

        cmake.definitions['BUILD_SHARED_LIBS'] = False
        cmake.definitions['CMAKE_SKIP_RPATH'] = True

        cmake.definitions['LLVM_TARGETS_TO_BUILD'] = self.options.targets
        cmake.definitions['LLVM_TARGET_ARCH'] = 'host'
        cmake.definitions['LLVM_BUILD_LLVM_DYLIB'] = self.options.shared
        cmake.definitions['LLVM_ENABLE_PIC'] = \
            self.options.get_safe('fPIC', default=False)
        cmake.definitions['LLVM_DYLIB_COMPONENTS'] = \
            self.options.get_safe('components', default='all')

        cmake.definitions['LLVM_ABI_BREAKING_CHECKS'] = 'WITH_ASSERTS'
        cmake.definitions['LLVM_ENABLE_WARNINGS'] = True
        cmake.definitions['LLVM_ENABLE_PEDANTIC'] = True
        cmake.definitions['LLVM_ENABLE_WERROR'] = False
        cmake.definitions['LLVM_ENABLE_LIBCXX'] = \
            'clang' in str(self.settings.compiler)

        cmake.definitions['LLVM_USE_RELATIVE_PATHS_IN_DEBUG_INFO'] = True
        cmake.definitions['LLVM_TEMPORARILY_ALLOW_OLD_TOOLCHAIN'] = False
        cmake.definitions['LLVM_BUILD_INSTRUMENTED_COVERAGE'] = False
        cmake.definitions['LLVM_OPTIMIZED_TABLEGEN'] = True
        cmake.definitions['LLVM_REVERSE_ITERATION'] = False
        cmake.definitions['LLVM_ENABLE_BINDINGS'] = False
        cmake.definitions['LLVM_CCACHE_BUILD'] = False

        cmake.definitions['LLVM_INCLUDE_TOOLS'] = self.options.shared
        cmake.definitions['LLVM_INCLUDE_EXAMPLES'] = False
        cmake.definitions['LLVM_INCLUDE_TESTS'] = False
        cmake.definitions['LLVM_INCLUDE_BENCHMARKS'] = False
        cmake.definitions['LLVM_APPEND_VC_REV'] = False
        cmake.definitions['LLVM_BUILD_DOCS'] = False
        cmake.definitions['LLVM_ENABLE_IDE'] = False

        cmake.definitions['LLVM_ENABLE_EH'] = self.options.exceptions
        cmake.definitions['LLVM_ENABLE_RTTI'] = self.options.rtti
        cmake.definitions['LLVM_ENABLE_THREADS'] = self.options.threads
        cmake.definitions['LLVM_ENABLE_LTO'] = self.options.lto
        cmake.definitions['LLVM_STATIC_LINK_CXX_STDLIB'] = \
            self.options.static_stdlib
        cmake.definitions['LLVM_ENABLE_UNWIND_TABLES'] = \
            self.options.unwind_tables
        cmake.definitions['LLVM_ENABLE_EXPENSIVE_CHECKS'] = \
            self.options.expensive_checks
        cmake.definitions['LLVM_ENABLE_ASSERTIONS'] = \
            self.settings.build_type == 'Debug'

        cmake.definitions['LLVM_USE_NEWPM'] = False
        cmake.definitions['LLVM_USE_OPROFILE'] = False
        cmake.definitions['LLVM_USE_PERF'] = self.options.use_perf

        cmake.definitions['LLVM_ENABLE_Z3_SOLVER'] = False
        cmake.definitions['LLVM_ENABLE_LIBPFM'] = False
        cmake.definitions['LLVM_ENABLE_LIBEDIT'] = False

        cmake.definitions['LLVM_ENABLE_ZLIB'] = \
            self.options.get_safe('with_zlib', False)
        cmake.definitions['LLVM_ENABLE_LIBXML2'] = \
            self.options.get_safe('with_xml2', False)
        cmake.definitions['LLVM_ENABLE_FFI'] = \
            self.options.get_safe('with_ffi', False)
        if self.options.get_safe('with_ffi', False):
            cmake.definitions['FFI_INCLUDE_DIR'] = \
                self.deps_cpp_info['libffi'].include_paths[0]
            cmake.definitions['FFI_LIBRARY_DIR'] = \
                self.deps_cpp_info['libffi'].lib_paths[0]
        return cmake

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
            del self.options.components
            del self.options.with_zlib
            del self.options.with_xml2
            del self.options.with_ffi

    def requirements(self):
        if self.options.get_safe('with_zlib', False):
            self.requires('zlib/1.2.11')
        if self.options.get_safe('with_xml2', False):
            self.requires('libxml2/2.9.10')
        if self.options.get_safe('with_ffi', False):
            self.requires('libffi/3.3')

    def configure(self):
        if self.settings.os == 'Windows' and self.options.shared:
            raise ConanInvalidConfiguration('shared lib not supported')
        if self.options.exceptions and not self.options.rtti:
            raise ConanInvalidConfiguration('exceptions require rtti support')

    def source(self):
        tools.get(**self.conan_data['sources'][self.version])
        source_path = Path(f'llvm-{self.version}.src')
        source_path.rename(self._source_subfolder)

        if self.version in self.conan_data['patches']:
            for patch in self.conan_data['patches'][self.version]:
                tools.patch(**patch)

    def build(self):
        cmake = self._configure_cmake()
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy('LICENSE.TXT', dst='licenses', src=self._source_subfolder)
        package_path = Path(self.package_folder)

        cmake = self._configure_cmake()
        cmake.install()

        if not self.options.shared:
            lib_regex = re.compile(
                r'add_library\((\w+?)\s.*?\)'
                r'(?:(?:#|\w|\s|\()+?'
                r'INTERFACE_LINK_LIBRARIES\s\"((?:;|:|/|\.|\w|\s|-|\(|\))+?)\"'
                r'(?:.|\n)*?\))?'
            )
            exports_file = 'LLVMExports.cmake'
            exports_path = package_path.joinpath('lib', 'cmake', 'llvm')
            exports_path = exports_path.joinpath(exports_file)

            exports = tools.load(str(exports_path.resolve()))
            exports = exports.replace(r'\$<LINK_ONLY:', '')
            exports = exports.replace(r'>', '')

            components = {}
            for match in re.finditer(lib_regex, exports):
                lib, deps = match.groups()
                if not lib.startswith('LLVM'):
                    continue

                components[lib] = []
                for dep in deps.split(';') if deps is not None else []:
                    if Path(dep).exists():
                        dep = Path(dep).stem.replace('lib', '')
                    elif dep.startswith('-delayload:'):
                        continue
                    components[lib].append(dep.replace('-l', ''))

        tools.rmdir(str(package_path.joinpath('bin').resolve()))
        tools.rmdir(str(package_path.joinpath('lib', 'cmake').resolve()))
        tools.rmdir(str(package_path.joinpath('share').resolve()))

        for file in package_path.joinpath('lib').iterdir():
            if 'LLVM' not in file.stem:
                file.unlink()

        if not self.options.shared:
            components_path = package_path.joinpath('lib', 'components.json')
            with components_path.open(mode='w') as file:
                json.dump(components, file, indent=4)
        else:
            for file in package_path.joinpath('lib').iterdir():
                for suffix in ['.dylib', '.so']:
                    if suffix not in file.suffixes:
                        file.unlink()

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = tools.collect_libs(self)
            if self.settings.os == 'Linux':
                self.cpp_info.system_libs = ['tinfo', 'pthread']
                self.cpp_info.system_libs.extend(['rt', 'dl', 'm'])
            elif self.settings.os == 'Macos':
                self.cpp_info.system_libs = ['curses', 'm']
            return

        package_path = Path(self.package_folder)
        components_path = package_path.joinpath('lib', 'components.json')
        with components_path.open(mode='r') as file:
            components = json.load(file)

        dependencies = ['z', 'iconv', 'xml2', 'ffi']
        targets = {
            'z': 'zlib::zlib',
            'xml2': 'libxml2::libxml2',
            'ffi': 'libffi::libffi'
        }

        for lib, deps in components.items():
            component = lib[4:].replace('LLVM', '').lower()

            self.cpp_info.components[component].libs = [lib]

            self.cpp_info.components[component].requires = [
                dep[4:].replace('LLVM', '').lower()
                for dep in deps if dep.startswith('LLVM')
            ]
            for lib, target in targets.items():
                if lib in deps:
                    self.cpp_info.components[component].requires.append(target)

            self.cpp_info.components[component].system_libs = [
                dep for dep in deps
                if not dep.startswith('LLVM') and dep not in dependencies
            ]
