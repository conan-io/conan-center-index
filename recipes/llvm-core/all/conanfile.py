from conans.errors import ConanInvalidConfiguration
from conans import ConanFile, CMake, tools

from pathlib import Path
from collections import defaultdict
import json
import re


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
        'with_ffi': [True, False],
        'with_zlib': [True, False],
        'with_xml2': [True, False]
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
        'with_ffi': False,
        'with_zlib': True,
        'with_xml2': True
    }

    exports_sources = ['CMakeLists.txt', 'patches/*']
    generators = ['cmake', 'cmake_find_package']
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return 'source'

    def _supports_compiler(self):
        compiler = self.settings.compiler.value
        version = tools.Version(self.settings.compiler.version)
        major_rev, minor_rev = int(version.major), int(version.minor)

        unsupported_combinations = [
            [compiler == 'gcc', major_rev == 5, minor_rev < 1],
            [compiler == 'gcc', major_rev < 5],
            [compiler == 'clang', major_rev < 4],
            [compiler == 'apple-clang', major_rev < 9],
            [compiler == 'Visual Studio', major_rev < 15]
        ]
        if any(all(combination) for combination in unsupported_combinations):
            message = 'unsupported compiler: "{}", version "{}"'
            raise ConanInvalidConfiguration(message.format(compiler, version))

    def _patch_sources(self):
        for patch in self.conan_data.get('patches', {}).get(self.version, []):
            tools.patch(**patch)

    def _patch_build(self):
        if Path('FindIconv.cmake').exists():
            tools.replace_in_file('FindIconv.cmake', 'iconv charset', 'iconv')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_SHARED_LIBS'] = False
        cmake.definitions['CMAKE_SKIP_RPATH'] = True

        cmake.definitions['LLVM_TARGETS_TO_BUILD'] = self.options.targets
        cmake.definitions['LLVM_TARGET_ARCH'] = 'host'
        cmake.definitions['LLVM_BUILD_LLVM_DYLIB'] = self.options.shared
        cmake.definitions['LLVM_DYLIB_COMPONENTS'] = self.options.components
        cmake.definitions['LLVM_ENABLE_PIC'] = \
            self.options.get_safe('fPIC', default=False)

        cmake.definitions['LLVM_ABI_BREAKING_CHECKS'] = 'WITH_ASSERTS'
        cmake.definitions['LLVM_ENABLE_WARNINGS'] = True
        cmake.definitions['LLVM_ENABLE_PEDANTIC'] = True
        cmake.definitions['LLVM_ENABLE_WERROR'] = False

        cmake.definitions['LLVM_TEMPORARILY_ALLOW_OLD_TOOLCHAIN'] = True
        cmake.definitions['LLVM_USE_RELATIVE_PATHS_IN_DEBUG_INFO'] = False
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
        cmake.definitions['LLVM_ENABLE_FFI'] = self.options.with_ffi
        cmake.definitions['LLVM_ENABLE_ZLIB'] = \
            self.options.get_safe('with_zlib', False)
        cmake.definitions['LLVM_ENABLE_LIBXML2'] = \
            self.options.get_safe('with_xml2', False)
        return cmake

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
            del self.options.with_zlib
            del self.options.with_xml2

    def requirements(self):
        if self.options.with_ffi:
            self.requires('libffi/3.3')
        if self.options.get_safe('with_zlib', False):
            self.requires('zlib/1.2.11')
        if self.options.get_safe('with_xml2', False):
            self.requires('libxml2/2.9.10')

    def configure(self):
        if self.settings.os == 'Windows' and self.options.shared:
            raise ConanInvalidConfiguration('shared lib not supported')
        if self.options.exceptions and not self.options.rtti:
            raise ConanInvalidConfiguration('exceptions require rtti support')
        self._supports_compiler()

    def source(self):
        tools.get(**self.conan_data['sources'][self.version])
        source_path = Path(f'llvm-{self.version}.src')
        source_path.rename(self._source_subfolder)
        self._patch_sources()

    def build(self):
        self._patch_build()
        cmake = self._configure_cmake()
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy('LICENSE.TXT', dst='licenses', src=self._source_subfolder)
        package_path = Path(self.package_folder)

        cmake = self._configure_cmake()
        cmake.install()

        if not self.options.shared:
            self.run('cmake --graphviz=graph/llvm.dot .')
            with tools.chdir('graph'):
                dot_text = tools.load('llvm.dot').replace('\r\n', '\n')

            dep_regex = re.compile(r'//\s(.+)\s->\s(.+)$', re.MULTILINE)
            deps = re.findall(dep_regex, dot_text)

            dummy_targets = defaultdict(list)
            for target, dep in deps:
                if not target.startswith('LLVM'):
                    dummy_targets[target].append(dep)

            cmake_targets = {
                'libffi::libffi': 'ffi',
                'ZLIB::ZLIB': 'z',
                'Iconv::Iconv': 'iconv',
                'LibXml2::LibXml2': 'xml2'
            }

            components = defaultdict(list)
            for lib, dep in deps:
                if not lib.startswith('LLVM'):
                    continue
                elif dep.startswith('-delayload:'):
                    continue
                elif dep.startswith('LLVM'):
                    components[dep]
                elif dep in cmake_targets:
                    dep = cmake_targets[dep]
                elif Path(dep).exists():
                    dep = Path(dep).stem.replace('lib', '')
                dep = dep.replace('-l', '')

                if dep in dummy_targets.keys():
                    components[lib].extend(dummy_targets[dep])
                    components[lib] = list(set(components[lib]))
                else:
                    components[lib].append(dep)

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
            suffixes = ['.dylib', '.so']
            for file in package_path.joinpath('lib').iterdir():
                if not any(suffix in file.suffixes for suffix in suffixes):
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

        dependencies = ['ffi', 'z', 'iconv', 'xml2']
        targets = {
            'ffi': 'libffi::libffi',
            'z': 'zlib::zlib',
            'xml2': 'libxml2::libxml2'
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
