from conans import ConanFile, tools, CMake
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration
import os, shutil, glob

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
        # check keep_binaries_regex early to fail early
        re.compile(str(self.options.keep_binaries_regex))
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
        },
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

    # XXX maybe check instead if part of lib folder ?
    def _is_relevant_component(self, target_name):
        return target_name.startswith('LLVM') or \
                target_name.startswith('clang') or \
                target_name.startswith('lldb') or \
                target_name.startswith('omp') or \
                target_name.startswith('lld') or \
                target_name.startswith('Polly') or \
                target_name == "LTO" or \
                target_name == "Remarks"
        # else ignored targets for llvm-14 with:
        # clang;clang-tools-extra;cross-project-tests;libc;libclc;lld;lldb;openmp;polly;pstl
        # compiler-rt;libcxx;libcxxabi;libunwind
        #
        # BugpointPasses ParallelSTL FileCheck
        # test_stdlib findAllSymbols elf_common libc_test_utils liblldb benchmark_main benchmark libc-benchmark libc-memory-benchmark
        # libc-memory-benchmark LibcFPTestHelpers LibcUnitTestMain libclang obj.clangTooling test_stdlib findAllSymbols
        # CheckerDependencyHandlingAnalyzerPlugin CheckerOptionHandlingAnalyzerPlugin SampleAnalyzerPlugin
        # DeLICMTests ISLToolsTests FlattenTests IslTests LibcUnitTest ScheduleOptimizerTests ScopPassManagerTests
        # pstl-pstl-header_inclusion_order.* pstl-pstl-version.pass pstl-std-algorithms-alg.* libc.* obj.*
        # ZLIB::ZLIB dl m rt pthread gtest gtest_main Threads::Threads json
        # -Wl,--version-script=/home/ubuntu/git/llvm-project/openmp/libomptarget/src/exports
        # -L/home/ubuntu/git/llvm-project/build/projects/libc/benchmarks/google-benchmark/lib/
        # /usr/lib/x86_64-linux-gnu/libcurses.so
        # /usr/lib/x86_64-linux-gnu/libform.so
        # /usr/lib/x86_64-linux-gnu/libpanel.so

    def package(self):
        cmake = self._cmake_configure()
        cmake.install()

        self.copy(
            "LICENSE.TXT",
            src=os.path.join(self._source_subfolder, "clang"),
            dst="licenses",
            keep_path=False,
        )

        binaries = []
        bin_matcher = re.compile(str(self.options.keep_binaries_regex))
        keep_binaries = []
        # resolve binaries to keep which are links, so we need to keep link target as well
        package_bin_path = os.path.join(self.package_folder, 'bin')
        for bin in os.listdir(package_bin_path):
            binaries.append(bin)
            # there are links like clang-14 -> clang -> clang++
            if bin_matcher.match(bin):
                keep_binaries.append(bin)
                current_bin=bin
                while os.path.islink(os.path.join('bin', current_bin)):
                    current_bin=os.path.basename(os.readlink(os.path.join('bin', current_bin)))
                    keep_binaries.append(current_bin)

        # remove unneccessary binaries from package
        for bin in binaries:
            if bin in keep_binaries:
                self.output.info(f"Keeping binary \"{bin}\" from package")
            else:
                self.output.info(f"Removing binary \"{bin}\" from package")
                os.remove(os.path.join(package_bin_path, bin))

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

        dummy_targets = defaultdict(list)
        for target, dep in deps:
            if not self._is_relevant_component(target):
                dummy_targets[target].append(dep)

        # map dependency names # XXX not seen any of this in llvm-14 linux build
        external_targets = {
            'libffi::libffi': 'ffi',
            'ZLIB::ZLIB': 'z',
            'Iconv::Iconv': 'iconv',
            'LibXml2::LibXml2': 'xml2'
        }
        
        # fill components with relevant targets
        components = defaultdict(list)
        for lib, dep in deps:
            if lib in binaries:
                continue
            if self._is_relevant_component(lib):
                # init relevant components
                components[lib]

                if isinstance(dep, list):
                    current_deps  = dep
                else:
                    current_deps  = [dep]

                visited = components[lib]
                while len(current_deps) > 0:
                    current_dep = current_deps.pop()
                    visited.append(current_dep)

                    if self._is_relevant_component(current_dep):
                        components[current_dep]

                    elif current_dep.startswith('-delayload:'): # special case from llvm-core but never seen, maybe other systems?
                        continue

                    # what !?
                    elif os.path.exists(current_dep):
                        s=os.path.basename(current_dep)
                        print(f"package debug, dep path exists: {s}") # TODO remove
                        current_dep = os.path.splitext(os.path.basename(current_dep))[0]
                        current_dep = current_dep.replace('lib', '')
                        print(f"exists: {current_dep} : {type(current_dep)}") # TODO remove

                    # e.g. -lpthread -> pthread
                    if current_dep.startswith("-l"):
                        current_dep = current_dep[2]


                    # if not relevant
                    if current_dep in dummy_targets.keys():
                        for d in dummy_targets[dep]:
                            if not visited:
                                current_deps.append(d)
                    elif self._is_relevant_component(dep):
                        components[lib].append(current_dep)
                    elif current_dep in external_targets:
                        components[lib].append(external_targets[current_dep])

            components[lib] = list(set(components[lib]))
            self.output.info(f"{lib} has {len(components[lib])} dependencies")
            if lib in components[lib]:
                self.output.warn("found circular dependency for {lib} over {dep}")
                components[lib].remove(lib)
        
        lib_path = os.path.join(self.package_folder, 'lib')
        if not self.options.shared:
            if self.options.get_safe('with_zlib', False):
                if not 'z' in components['LLVMSupport']:
                    components['LLVMSupport'].append('z')
        else:
            suffixes = ['.dylib', '.so']
            for name in os.listdir(lib_path):
                if not any(suffix in name for suffix in suffixes):
                    os.remove(os.path.join(lib_path, name))

        components_path = os.path.join(self.package_folder, 'lib', 'components.json')
        with open(components_path, 'w') as components_file:
            json.dump(components, components_file, indent=4)

    def package_id(self):
        del self.info.options.enable_debug
        del self.info.options.use_llvm_cmake_files

    def validate(self):
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

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.builddirs = ["lib/cmake"]
