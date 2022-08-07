from conans import ConanFile, tools, CMake
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration
from collections import defaultdict
import os, shutil, glob, re, json

# https://llvm.org/docs/CMake.html#frequently-used-llvm-related-variables
projects = [
    'clang',
    'clang-tools-extra',
    'libc',
    'libclc',
    'lld',
    'lldb',
    'openmp',
    'polly',
    'pstl',
]
runtimes = [
    'compiler-rt',
    'libc',
    'libcxx',
    'libcxxabi',
    'libunwind',
    'openmp',
]
default_projects = [
    'clang',
    'clang-tools-extra',
    #'libc', clang-14 crashes for sin/cos/tan
    'libclc',
    'lld',
    'lldb',
    'openmp',
    'polly',
    'pstl',
]
default_runtimes = [
    # 'compiler-rt', # include missing
    # 'libc',
    'libcxx',
    'libcxxabi',
    'libunwind',
]

class Llvm(ConanFile):
    name = 'llvm'
    description = 'The LLVM Project is a collection of modular and reusable compiler and toolchain technologies'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://github.com/llvm/llvm-project'
    license = 'Apache-2.0'
    topics = 'cpp', 'compiler', 'tooling', 'clang'

    settings = 'os', 'arch', 'compiler', 'build_type'

    no_copy_source = True
    _source_subfolder = 'source'
    short_paths = True
    exports_sources = 'patches/**/*'

    options = {
        **{'with_project_' + project: [True, False]
           for project in projects},
        **{"with_runtime_" + runtime: [True, False]
           for runtime in runtimes},
        **{
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
            'with_z3': [True, False],
            'with_ffi': [True, False],
            'with_zlib': [True, False], # ? https://conan.io/center/zlib
            'with_xml2': [True, False], # ? https://conan.io/center/libxml2
            'use_llvm_cmake_files': [True, False],
            'enable_debug': [True, False],
            'keep_binaries_regex': 'ANY',
        },
    }
    default_options = {
        **{
            'with_project_' + project: project in default_projects
            for project in projects
        },
        **{
            "with_runtime_" + runtime: runtime in default_runtimes
            for runtime in runtimes
        },
        **{
            'shared': False,
            'fPIC': True,
            'components': 'all',
            'targets': 'all',
            'exceptions': True, # llvm 14 default off
            'rtti': True, # llvm 14 default off
            'threads': True,
            'lto': 'Off',
            'static_stdlib': False,
            'unwind_tables': True,
            'expensive_checks': False,
            'use_perf': False,
            'use_sanitizer': 'None',
            'with_z3': False,
            'with_ffi': False,
            'with_zlib': True,
            'with_xml2': True,
            'enable_debug': False,
            'use_llvm_cmake_files': False,
            'keep_binaries_regex': '^(clang\+\+|clang|opt)$',
        }
    }
    generators = 'cmake_find_package'

    def requirements(self):
        if self.options.with_ffi:
            self.requires('libffi/3.4.2')
        if self.options.get_safe('with_zlib', False):
            self.requires('zlib/1.2.12')
        if self.options.get_safe('with_xml2', False):
           self.requires('libxml2/2.9.10')
        if self.options.get_safe('with_z3', False):
            self.requires('z3/4.8.8')

    @property
    def repo_folder(self):
        return os.path.join(self.source_folder, self._source_subfolder)

    def project_folder(self, project):
        return os.path.join(self.repo_folder, project)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = 'llvm-project-llvmorg-' + self.version
        os.rename(extracted_dir, self._source_subfolder)
        self._patch_sources()

    def build_requirements(self):
        # Older cmake versions may have issues generating the graphviz output used
        # to model the components
        self.build_requires("cmake/3.21.3")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_zlib
            del self.options.with_xml2
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, '14')

    def _patch_sources(self):
        for patch in self.conan_data.get('patches', {}).get(self.version, []):
            tools.patch(**patch)

        # fix LOCATION / LOCATION_${build_type} not set on libxml2
        tools.replace_in_file(self._source_subfolder + "/llvm/lib/WindowsManifest/CMakeLists.txt", "get_property", 'find_library(libxml2_library NAME xml2 PATHS ${LibXml2_LIB_DIRS} NO_DEFAULT_PATH NO_CMAKE_FIND_ROOT_PATH) #')

    def _cmake_configure(self):
        enabled_projects = [
            project for project in projects
            if getattr(self.options, 'with_project_' + project)
        ]
        enabled_runtimes = [
            runtime for runtime in runtimes
            if getattr(self.options, 'with_runtime_' + runtime)
        ]
        self.output.info('Enabled LLVM subprojects: {}'.format(
            ', '.join(enabled_projects)))
        self.output.info('Enabled LLVM runtimes: {}'.format(
            ', '.join(enabled_runtimes)))

        cmake = CMake(self, generator="Ninja", parallel=False)
        cmake.configure(
            args=['--graphviz=graph/llvm.dot'],
            defs={
                'BUILD_SHARED_LIBS': False,
                'CMAKE_SKIP_RPATH': True,
                'CMAKE_POSITION_INDEPENDENT_CODE': \
                    self.options.get_safe('fPIC', default=False) or self.options.shared,
                'LLVM_TARGET_ARCH': 'host',
                'LLVM_TARGETS_TO_BUILD': self.options.targets,
                'LLVM_BUILD_LLVM_DYLIB': self.options.shared,
                'LLVM_DYLIB_COMPONENTS': self.options.components,
                'LLVM_ENABLE_PIC': self.options.get_safe('fPIC', default=False),
                'LLVM_ABI_BREAKING_CHECKS': 'WITH_ASSERTS',
                'LLVM_ENABLE_WARNINGS': True,
                'LLVM_ENABLE_PEDANTIC': True,
                'LLVM_ENABLE_WERROR': False,
                'LLVM_TEMPORARILY_ALLOW_OLD_TOOLCHAIN': True,
                'LLVM_USE_RELATIVE_PATHS_IN_DEBUG_INFO': False,
                'LLVM_BUILD_INSTRUMENTED_COVERAGE': False,
                'LLVM_OPTIMIZED_TABLEGEN': True, # NOT default, can speedup compilation a lot
                'LLVM_REVERSE_ITERATION': False,
                'LLVM_ENABLE_BINDINGS': False, # NOT default, dont build OCaml and go bindings
                'LLVM_CCACHE_BUILD': False,
                'LLVM_INCLUDE_TOOLS': True, # needed for clang libs, but remove binaries
                'LLVM_INCLUDE_EXAMPLES': False, # NOT default
                'LLVM_BUILD_TESTS': False,
                'LLVM_INCLUDE_TESTS': False, # NOT default
                'LLVM_INCLUDE_BENCHMARKS': False,
                'LLVM_APPEND_VC_REV': True,
                'LLVM_BUILD_DOCS': False,
                'LLVM_ENABLE_IDE': False,
                'LLVM_ENABLE_TERMINFO': False, # NOT default Use terminfo database if available.
                'LLVM_ENABLE_EH': self.options.exceptions,
                'LLVM_ENABLE_RTTI': self.options.rtti,
                'LLVM_ENABLE_THREADS': self.options.threads,
                'LLVM_ENABLE_LTO': self.options.lto,
                'LLVM_STATIC_LINK_CXX_STDLIB': self.options.static_stdlib,
                'LLVM_ENABLE_UNWIND_TABLES': self.options.unwind_tables,
                'LLVM_ENABLE_EXPENSIVE_CHECKS': self.options.expensive_checks,
                'LLVM_ENABLE_ASSERTIONS': self.settings.build_type == 'Debug',
                'LLVM_USE_NEWPM': False,
                'LLVM_USE_OPROFILE': False,
                'LLVM_USE_PERF': self.options.use_perf,
                'LLVM_ENABLE_Z3_SOLVER': self.options.with_z3,
                'LLVM_ENABLE_LIBPFM': False,
                'LLVM_ENABLE_LIBEDIT': False,
                'LLVM_ENABLE_FFI': self.options.with_ffi,
                'LLVM_ENABLE_ZLIB': self.options.get_safe('with_zlib', False),
                'LLVM_ENABLE_LIBXML2': self.options.get_safe('with_xml2', False),
                'LLVM_ENABLE_PROJECTS': ';'.join(enabled_projects),
                'LLVM_ENABLE_RUNTIMES': ';'.join(enabled_runtimes),
            }, 
            source_folder=os.path.join(self._source_subfolder, 'llvm'))
        if not self.options.shared:
            cmake.definitions['DISABLE_LLVM_LINK_LLVM_DYLIB'] = True
        if self.settings.compiler == 'Visual Studio':
            build_type = str(self.settings.build_type).upper()
            cmake.definitions['LLVM_USE_CRT_{}'.format(build_type)] = \
                self.settings.compiler.runtime
        if self.options.use_sanitizer == 'None':
            cmake.definitions['LLVM_USE_SANITIZER'] = ''
        else:
            cmake.definitions['LLVM_USE_SANITIZER'] = self.options.use_sanitizer
        return cmake

    def build(self):
        cmake = self._cmake_configure()
        cmake.build()

    def _is_relevant_component(self, target_name):
        package_lib_folder = os.path.join(self.package_folder, "lib")
        return os.path.exists(os.path.join(package_lib_folder, f"lib{target_name}.a")) or \
                os.path.exists(os.path.join(package_lib_folder, f"lib{target_name}.so")) or \
                os.path.exists(os.path.join(package_lib_folder, f"lib{target_name}.dylib"))

    def package(self):
        cmake = self._cmake_configure()
        cmake.install()

        self.copy(
            "LICENSE.TXT",
            src=os.path.join(self._source_subfolder, "clang"),
            dst="licenses",
            keep_path=False,
        )

        bin_matcher = re.compile(str(self.options.keep_binaries_regex))
        keep_binaries = []
        # resolve binaries to keep which are links, so we need to keep link target as well
        build_bin_path = os.path.join(self.build_folder, 'bin')
        binaries = ["lldb-test", "clang-fuzzer", "clang-objc-fuzzer"] # missed by the method below
        binaries.extend(os.listdir(build_bin_path))
        binaries.extend(os.listdir(os.path.join(self.package_folder, 'bin')))
        binaries = list(set(binaries))
        for bin in binaries:
            if bin_matcher.match(bin):
                keep_binaries.append(bin)
                current_bin=bin
                # there are links like clang-14 -> clang -> clang++
                while os.path.islink(os.path.join('bin', current_bin)):
                    current_bin=os.path.basename(os.readlink(os.path.join('bin', current_bin)))
                    keep_binaries.append(current_bin)

        # remove unneccessary binaries from package
        package_bin_path = os.path.join(self.build_folder, 'bin')
        for bin in binaries:
            bin_path = os.path.join(package_bin_path, bin)
            if bin in keep_binaries:
                self.output.info(f"Keeping binary \"{bin}\" from package")
            elif os.path.isfile(bin_path):
                self.output.info(f"Removing binary \"{bin}\" from package")
                os.remove(bin_path)

        # remove unneccessary files from package
        ignore = ["share", "libexec", "**/Find*.cmake", "**/*Config.cmake"]
        for ignore_entry in ignore:
            ignore_glob = os.path.join(self.package_folder, ignore_entry)

            for ignore_path in glob.glob(ignore_glob, recursive=True):
                self.output.info('Removing ignored file/directory "{}" from package'.format(ignore_path))

                if os.path.isfile(ignore_path):
                    os.remove(ignore_path)
                else:
                    shutil.rmtree(ignore_path)
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))

        # remove binaries from build, in debug builds these can take 40gb of disk space but are fast to recreate
        tools.rmdir(os.path.join(self.build_folder, 'bin'))
        
        if not self.options.shared:
            for ext in ['.a', '.lib']:
                lib = '**/lib/*LLVMTableGenGlobalISel{}'.format(ext)
                self.copy(lib, dst='lib', keep_path=False)
                lib = '*LLVMTableGenGlobalISel{}'.format(ext)
                self.copy(lib, dst='lib', src='lib')

        # creating dependency graph
        with tools.chdir('graph'):
            dot_text = tools.load('llvm.dot').replace('\r\n', '\n')
        dep_regex = re.compile(r'//\s(.+)\s->\s(.+)$', re.MULTILINE)
        deps = re.findall(dep_regex, dot_text)

        # map dependency names # XXX not seen any of this in llvm-14 linux build
        external_targets = {
            'libffi::libffi': 'ffi',
            'ZLIB::ZLIB': 'z',
            'Iconv::Iconv': 'iconv',
            'LibXml2::LibXml2': 'xml2',
            'pthread': 'pthread',
            'rt': "rt",
            'm': "m",
            'dl': 'dl'
        } 
        external_targets_keys = external_targets.keys()
        dummy_targets = defaultdict(list)
        for target, dep in deps:
            if not self._is_relevant_component(target) and target not in external_targets_keys:
                dummy_targets[target].append(dep)
        dummy_targets_keys = dummy_targets.keys()
        
        # fill components with relevant targets
        components = defaultdict(list)
        ignored_deps = []
        for lib, dep in deps:
            if lib in binaries:
                continue

            if self._is_relevant_component(lib):
                components[lib]

                if isinstance(dep, list):
                    current_deps  = dep
                elif " " in dep:
                    current_deps = dep.split() # lib: omp dep: str(-lpthread -lrt)
                else:
                    current_deps  = [dep]
                
                visited = components[lib].copy()
                while len(current_deps) > 0:
                    current_dep = current_deps.pop()
                    visited.append(current_dep)

                    if current_dep in binaries:
                        continue
                    elif self._is_relevant_component(current_dep):
                        components[current_dep]

                    # Copied from llvm-core but not used on linus, maybe for other systems? ==>
                    elif current_dep.startswith('-delayload:'):
                        continue

                    elif os.path.exists(current_dep):
                        current_dep = os.path.splitext(os.path.basename(current_dep))[0]
                        current_dep = current_dep.replace('lib', '')
                    # <==

                    if current_dep.startswith("-l"): # e.g. -lpthread -> pthread
                        current_dep = current_dep[2:]

                    if current_dep in dummy_targets_keys:
                        for d in dummy_targets[current_dep]:
                            if not visited:
                                current_deps.append(d)
                    elif self._is_relevant_component(current_dep):
                        if not self.options.shared:
                            components[lib].append(current_dep)
                    elif current_dep in external_targets_keys:
                        components[lib].append(external_targets[current_dep])
                    else:
                        ignored_deps.append(current_dep)
                components[lib] = list(set(components[lib]))
                if lib in components[lib]:
                    raise "found circular dependency for {lib} over {dep}"
        ignored_deps = list(set(ignored_deps))
        self.output.info(f'ignored these dependencies: {ignored_deps}')

        # workaround for circular dependencies
        remove_dependencies = [
            ('lldbBreakpoint', 'lldbCore'),
            ('lldbBreakpoint', 'lldbTarget'),
            ('lldbPluginCPlusPlusLanguage', 'lldbCore'),
            ('lldbPluginObjCLanguage', 'lldbCore'),
            ('lldbTarget', 'lldbCore'),
            ('lldbInterpreter', 'lldbCore'),
            ('lldbSymbol', 'lldbCore'),
            ('lldbDataFormatters', 'lldbCore'),
            ('lldbExpression', 'lldbCore'),
            ('lldbDataFormatters', 'lldbInterpreter'),
            ('lldbTarget', 'lldbInterpreter'),
            ('lldbInterpreter', 'lldbCommands'),
            ('lldbCommands', 'lldbInterpreter'),
            ('lldbExpression', 'lldbTarget'),
            ('lldbExpression', 'lldbSymbol'),
            ('lldbSymbol', 'lldbTarget'),
            ('lldbSymbol', 'lldbExpression'),
            ('lldbTarget', 'lldbSymbol'),
            ('lldbTarget', 'lldbPluginProcessUtility'),
            ('lldbTarget', 'lldbExpression'),
            ('lldbPluginProcessUtility', 'lldbTarget'),
            ('lldbPluginExpressionParserClang', 'lldbPluginTypeSystemClang'),
            ('lldbPluginTypeSystemClang', 'lldbPluginSymbolFileDWARF'),
            ('lldbPluginTypeSystemClang', 'lldbPluginExpressionParserClang'),
            ('lldbPluginTypeSystemClang', 'lldbPluginSymbolFilePDB'),
            ('lldbPluginSymbolFileDWARF', 'lldbPluginTypeSystemClang'),
            ('lldbPluginSymbolFilePDB', 'lldbPluginTypeSystemClang'),
            ('lldbPluginDynamicLoaderPosixDYLD', 'lldbPluginProcessElfCore'),
            ('lldbPluginProcessElfCore', 'lldbPluginDynamicLoaderPosixDYLD'),
        ]
        keys = components.keys() 

        for target, remove in remove_dependencies:
            if target in keys:
                if remove in components[target]:
                    components[target].remove(remove)
                if target in components[remove]:
                    components[remove].remove(target)
        r = False
        for c in keys:
            for c_dep in components[c]:
                if c_dep in keys:
                    if c in components[c_dep]:
                        self.output.warn(f"{c} -> {c_dep} -> {c}")
                        r = True
        if r:
            raise "circulare dependency found"
        
        lib_path = os.path.join(self.package_folder, 'lib')
        if not self.options.shared:
            if self.options.get_safe('with_zlib', False):
                if not 'z' in components['LLVMSupport']:
                    components['LLVMSupport'].append('z')
        else:
            suffixes = ['.dylib', '.so']
            for name in os.listdir(lib_path):
                if not any(suffix in name for suffix in suffixes):
                    remove_path = os.path.join(lib_path, name)
                    self.output.info(f"Removing library \"{remove_path}\" from package because its not shared")
                    if os.path.isfile(remove_path):
                        os.remove(remove_path)
                    else:
                        shutil.rmtree(remove_path)

            # because we remove libs from lib/folder, we need to clear components as well
            removed = []
            for key in components.keys():
                removed_component = not self._is_relevant_component(key)
                if removed_component:
                    removed.append(key)
            for remove in removed:
                del components[remove]
            # and check if still existing components relay on these
            for remove in removed:
                for key in components.keys():
                    if remove in components[key]:
                        self.output.info(f"Removing dependency from \"{key}\" to \"{remove}\" because its not available as shared.")
                        components[key].remove(remove)
        
        # write components.json for package_info
        components_path = os.path.join(self.package_folder, 'lib', 'components.json')
        with open(components_path, 'w') as components_file:
            json.dump(components, components_file, indent=4)

    def package_id(self):
        del self.info.options.enable_debug
        del self.info.options.use_llvm_cmake_files

    def validate(self):
        # check keep_binaries_regex early to fail early
        re.compile(str(self.options.keep_binaries_regex))

        if self.settings.compiler == "gcc" and tools.Version(
                self.settings.compiler.version) < "10":
            raise ConanInvalidConfiguration(
                "Compiler version too low for this package.")

        if (self.settings.compiler == "Visual Studio"
                or self.settings.compiler == "msvc") and Version(
                    self.settings.compiler.version) < "16.4":
            raise ConanInvalidConfiguration(
                "An up to date version of Microsoft Visual Studio 2019 or newer is required."
            )

        if self.settings.build_type == "Debug" and not self.options.enable_debug:
            raise ConanInvalidConfiguration(
                "Set the 'enable_debug' option to allow debug builds")
        
        for project in projects:
            for runtime in runtimes:
                if project == runtime and \
                    self.options.get_safe('with_project_' + project, False) and self.options.get_safe('with_runtime_' + runtime, False):
                    raise ConanInvalidConfiguration(f"Duplicate entry in enabled projects / runtime found for \"with_project_{project}\"")

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

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
        external_targets = {
            'ffi': 'libffi::libffi',
            'z': 'zlib::zlib',
            'xml2': 'libxml2::libxml2',
            'iconv': 'Iconv::Iconv',
        }

        for component, deps in components.items():
            self.cpp_info.components[component].libs = [component]
            self.cpp_info.components[component].requires.extend(dep for dep in deps if self._is_relevant_component(dep))

            for lib, target in external_targets.items():
                if lib in deps:
                    self.cpp_info.components[component].requires.append(target)

            self.cpp_info.components[component].system_libs = [
                dep for dep in deps
                if not self._is_relevant_component(dep) and dep not in dependencies
            ]

            self.cpp_info.components[component].set_property("cmake_target_name", component)
            self.cpp_info.components[component].builddirs.append(self._module_subfolder)
            self.cpp_info.components[component].names["cmake_find_package"] = component
            self.cpp_info.components[component].names["cmake_find_package_multi"] = component

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