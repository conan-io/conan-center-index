from conan.errors import ConanInvalidConfiguration
from conans import ConanFile, CMake, tools
from collections import defaultdict
import json
import re
import os.path
import os
import textwrap

required_conan_version = ">=1.33.0"


class LLVMCoreConan(ConanFile):
    name = 'llvm-core'
    description = (
        'A toolkit for the construction of highly optimized compilers,'
        'optimizers, and runtime environments.'
    )
    license = 'Apache-2.0 WITH LLVM-exception'
    topics = ('llvm', 'compiler')
    homepage = 'https://llvm.org'
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
        'use_sanitizer': [
            'Address',
            'Memory',
            'MemoryWithOrigins',
            'Undefined',
            'Thread',
            'DataFlow',
            'Address;Undefined',
            'None'
        ],
        'with_ffi': [True, False],
        'with_zlib': [True, False],
        'with_xml2': [True, False],
        'use_llvm_cmake_files': [True, False],
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
        'use_sanitizer': 'None',
        'with_ffi': False,
        'with_zlib': True,
        'with_xml2': True,
        'use_llvm_cmake_files': False,
    }

    # Older cmake versions may have issues generating the graphviz output used
    # to model the components
    build_requires = [
        'cmake/3.20.5'
    ]

    generators = 'cmake', 'cmake_find_package'
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
        if os.path.exists('FindIconv.cmake'):
            tools.replace_in_file('FindIconv.cmake', 'iconv charset', 'iconv')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['BUILD_SHARED_LIBS'] = False
        cmake.definitions['CMAKE_SKIP_RPATH'] = True
        cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = \
            self.options.get_safe('fPIC', default=False) or self.options.shared

        if not self.options.shared:
            cmake.definitions['DISABLE_LLVM_LINK_LLVM_DYLIB'] = True
        # cmake.definitions['LLVM_LINK_DYLIB'] = self.options.shared

        cmake.definitions['LLVM_TARGET_ARCH'] = 'host'
        cmake.definitions['LLVM_TARGETS_TO_BUILD'] = self.options.targets
        cmake.definitions['LLVM_BUILD_LLVM_DYLIB'] = self.options.shared
        cmake.definitions['LLVM_DYLIB_COMPONENTS'] = self.options.components
        cmake.definitions['LLVM_ENABLE_PIC'] = \
            self.options.get_safe('fPIC', default=False)

        if self.settings.compiler == 'Visual Studio':
            build_type = str(self.settings.build_type).upper()
            cmake.definitions['LLVM_USE_CRT_{}'.format(build_type)] = \
                self.settings.compiler.runtime

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
        cmake.definitions['LLVM_ENABLE_TERMINFO'] = False

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
        if self.options.use_sanitizer == 'None':
            cmake.definitions['LLVM_USE_SANITIZER'] = ''
        else:
            cmake.definitions['LLVM_USE_SANITIZER'] = \
                self.options.use_sanitizer

        cmake.definitions['LLVM_ENABLE_Z3_SOLVER'] = False
        cmake.definitions['LLVM_ENABLE_LIBPFM'] = False
        cmake.definitions['LLVM_ENABLE_LIBEDIT'] = False
        cmake.definitions['LLVM_ENABLE_FFI'] = self.options.with_ffi
        cmake.definitions['LLVM_ENABLE_ZLIB'] = \
            self.options.get_safe('with_zlib', False)
        cmake.definitions['LLVM_ENABLE_LIBXML2'] = \
            self.options.get_safe('with_xml2', False)
        return cmake

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
            del self.options.with_zlib
            del self.options.with_xml2

    def requirements(self):
        if self.options.with_ffi:
            self.requires('libffi/3.3')
        if self.options.get_safe('with_zlib', False):
            self.requires('zlib/1.2.12')
        if self.options.get_safe('with_xml2', False):
            self.requires('libxml2/2.9.10')

    def package_id(self):
        del self.info.options.use_llvm_cmake_files

    def validate(self):
        if self.options.shared:  # Shared builds disabled just due to the CI
            message = 'Shared builds not currently supported'
            raise ConanInvalidConfiguration(message)
            # del self.options.fPIC
        # if self.settings.os == 'Windows' and self.options.shared:
        #     message = 'Shared builds not supported on Windows'
        #     raise ConanInvalidConfiguration(message)
        if self.options.exceptions and not self.options.rtti:
            message = 'Cannot enable exceptions without rtti support'
            raise ConanInvalidConfiguration(message)
        self._supports_compiler()
        if tools.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration('Cross-building not implemented')

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)
        self._patch_sources()

    def build(self):
        self._patch_build()
        cmake = self._configure_cmake()
        cmake.configure()
        cmake.build()

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake", "llvm")

    @property
    def _alias_module_file_rel_path(self):
        return os.path.join(self._module_subfolder, "conan-official-{}-targets.cmake".format(self.name))

    @property
    def _old_alias_module_file_rel_path(self):
        return os.path.join(self._module_subfolder, "conan-official-{}-old-targets.cmake".format(self.name))

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    def package(self):
        self.copy('LICENSE.TXT', dst='licenses', src=self._source_subfolder)
        lib_path = os.path.join(self.package_folder, 'lib')

        cmake = self._configure_cmake()
        cmake.install()

        if not self.options.shared:
            for ext in ['.a', '.lib']:
                lib = '**/lib/*LLVMTableGenGlobalISel{}'.format(ext)
                self.copy(lib, dst='lib', keep_path=False)
                lib = '*LLVMTableGenGlobalISel{}'.format(ext)
                self.copy(lib, dst='lib', src='lib')

            CMake(self).configure(args=['--graphviz=graph/llvm.dot'], source_dir='.', build_dir='.')
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
                elif os.path.exists(dep):
                    dep = os.path.splitext(os.path.basename(dep))[0]
                    dep = dep.replace('lib', '')
                dep = dep.replace('-l', '')

                if dep in dummy_targets.keys():
                    components[lib].extend(dummy_targets[dep])
                    components[lib] = list(set(components[lib]))
                else:
                    components[lib].append(dep)

            alias_targets = {}
            old_alias_targets = {}
            for component, _ in components.items():
                alias_targets[component] = "LLVM::{}".format(component)
                old_alias_targets["llvm-core::{}".format(component[4:].replace('LLVM', '').lower())] = "LLVM::{}".format(component)

            # TODO: to remove in conan v2 once cmake_find_package_* generators removed
            self._create_cmake_module_alias_targets(
                os.path.join(self.package_folder, self._alias_module_file_rel_path),
                alias_targets
            )

            self._create_cmake_module_alias_targets(
                os.path.join(self.package_folder, self._old_alias_module_file_rel_path),
                old_alias_targets
            )

        tools.rmdir(os.path.join(self.package_folder, 'share'))

        tools.remove_files_by_mask(self.package_folder, "LLVMExports*.cmake")
        tools.rename(os.path.join(self.package_folder, self._module_subfolder, 'LLVM-Config.cmake'),
                     os.path.join(self.package_folder, self._module_subfolder, 'LLVM-ConfigInternal.cmake'))
        tools.rename(os.path.join(self.package_folder, self._module_subfolder, 'LLVMConfig.cmake'),
                     os.path.join(self.package_folder, self._module_subfolder, 'LLVMConfigInternal.cmake'))

        tools.replace_in_file(os.path.join(self.package_folder, self._module_subfolder, 'AddLLVM.cmake'),
                              "include(LLVM-Config)",
                              "include(LLVM-ConfigInternal)")
        tools.replace_in_file(os.path.join(self.package_folder, self._module_subfolder, 'LLVMConfigInternal.cmake'),
                              "LLVM-Config.cmake",
                              "LLVM-ConfigInternal.cmake")

        for mask in ["Find*.cmake", "*Config.cmake", "*-config.cmake"]:
            tools.remove_files_by_mask(self.package_folder, mask)

        for name in os.listdir(lib_path):
            fullname = os.path.join(lib_path, name)
            if 'LLVM' not in name and os.path.isfile(fullname):
                os.remove(fullname)

        if not self.options.shared:
            if self.options.get_safe('with_zlib', False):
                if not 'z' in components['LLVMSupport']:
                    components['LLVMSupport'].append('z')
            components_path = \
                os.path.join(self.package_folder, 'lib', 'components.json')
            with open(components_path, 'w') as components_file:
                json.dump(components, components_file, indent=4)
        else:
            suffixes = ['.dylib', '.so']
            for name in os.listdir(lib_path):
                if not any(suffix in name for suffix in suffixes):
                    os.remove(os.path.join(lib_path, name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LLVM")

        if self.options.shared:
            self.cpp_info.libs = tools.collect_libs(self)
            if self.settings.os == 'Linux':
                self.cpp_info.system_libs = ['pthread', 'rt', 'dl', 'm']
            elif self.settings.os == 'Macos':
                self.cpp_info.system_libs = ['m']
            return

        components_path = \
            os.path.join(self.package_folder, 'lib', 'components.json')
        with open(components_path, 'r') as components_file:
            components = json.load(components_file)

        dependencies = ['ffi', 'z', 'iconv', 'xml2']
        targets = {
            'ffi': 'libffi::libffi',
            'z': 'zlib::zlib',
            'xml2': 'libxml2::libxml2'
        }

        for component, deps in components.items():
            self.cpp_info.components[component].libs = [component]
            self.cpp_info.components[component].requires.extend(dep for dep in deps if dep.startswith('LLVM'))

            for lib, target in targets.items():
                if lib in deps:
                    self.cpp_info.components[component].requires.append(target)

            self.cpp_info.components[component].system_libs = [
                dep for dep in deps
                if not dep.startswith('LLVM') and dep not in dependencies
            ]

            self.cpp_info.components[component].set_property("cmake_target_name", component)
            self.cpp_info.components[component].builddirs.append(self._module_subfolder)

            self.cpp_info.components[component].names["cmake_find_package"] = component
            self.cpp_info.components[component].names["cmake_find_package_multi"] = component
            self.cpp_info.components[component].build_modules["cmake_find_package"].extend([
                self._alias_module_file_rel_path,
                self._old_alias_module_file_rel_path,
            ])
            self.cpp_info.components[component].build_modules["cmake_find_package_multi"].extend([
                self._alias_module_file_rel_path,
                self._old_alias_module_file_rel_path,
            ])

            if self.options.use_llvm_cmake_files:
                self.cpp_info.components[component].build_modules["cmake_find_package"].append(
                    os.path.join(self._module_subfolder, "LLVMConfigInternal.cmake")
                )
                self.cpp_info.components[component].build_modules["cmake_find_package_multi"].append(
                    os.path.join(self._module_subfolder, "LLVMConfigInternal.cmake")
                )

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "LLVM"
        self.cpp_info.names["cmake_find_package_multi"] = "LLVM"
