from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake
from conan.tools.files import get, apply_conandata_patches, rmdir, chdir, load, collect_libs
from conan.tools.microsoft import is_msvc
from conan.tools.files.copy_pattern import copy
from conan.tools.build.cppstd import check_min_cppstd
from conan.tools.system.package_manager import Apt
from conan.errors import ConanInvalidConfiguration
from collections import defaultdict
from conan.tools.cmake.layout import cmake_layout
from conan.errors import ConanException
import os
import shutil
import glob
import re
import json

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
    # 'libc', # clang-14 crashes for sin/cos/tan for 13.0.0-14.0.6
    'libclc',
    'lld',
    # TODO: lib/liblldb.so.14.0.6 / libxml2, error: undefined symbol: libiconv_open, referenced by encoding.c in libxml2.a
    # probably because libxml2 isn't migrated to conan2, maybe components['lldbHost'].requires.append('Iconv::Iconv') ?
    # 'lldb',
    'openmp',
    'polly',
    'pstl',
]
default_runtimes = [
    # 'compiler-rt',  # fatal error: 'bits/libc-header-start.h' file not found
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

    # XXX Conan1 dont copy source to build directory, large software opt
    no_copy_source = True
    short_paths = True  # XXX Conan1 short paths for windows, no longer needed for recent win10

    options = {
        **{'with_project_' + project: [True, False]
           for project in projects},
        **{"with_runtime_" + runtime: [True, False]
           for runtime in runtimes},
        **{
            'shared': [True, False],
            'llvm_build_llvm_dylib': [True, False],
            'llvm_link_llvm_dylib': [True, False],
            'llvm_dylib_components': ['ANY'],
            'fPIC': [True, False],
            'targets': ['ANY'],
            'exceptions': [True, False],
            'rtti': [True, False],
            'threads': [True, False],
            'lto': ['On', 'Off', 'Full', 'Thin'],
            'static_stdlib': [True, False],
            'unwind_tables': [True, False],
            'expensive_checks': [True, False],
            'use_perf': [True, False],
            'llvm_use_sanitizer': [
                'Address',
                'Memory',
                'MemoryWithOrigins',
                'Undefined',
                'Thread',
                'DataFlow',
                'Address;Undefined',
                ''
            ],
            'with_z3': [True, False],
            'with_ffi': [True, False],
            'with_zlib': [True, False],
            'with_xml2': [True, False],
            'keep_binaries_regex': ['ANY'],

            # options removed in package id
            'use_llvm_cmake_files': [True, False],
            'enable_debug': [True, False],
            'clean_build_bin': [True, False],
            'ram_per_compile_job': ['ANY'],
            'ram_per_link_job': ['ANY'],
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
            'llvm_build_llvm_dylib': False,
            'llvm_link_llvm_dylib': False,
            'llvm_dylib_components': 'all',
            'fPIC': True,
            'targets': 'all',
            'exceptions': True,  # llvm 14 default off
            'rtti': True,  # llvm 14 default off
            'threads': True,
            'lto': 'Off',
            'static_stdlib': False,
            'unwind_tables': True,
            'expensive_checks': False,
            'use_perf': False,
            'llvm_use_sanitizer': '',
            'with_z3': False,
            'with_ffi': False,
            'with_zlib': True,
            'with_xml2': True,
            'keep_binaries_regex': '^$',

            # options removed in package id
            # disable debug builds in ci XXX remove because only used for debugging ci?
            'enable_debug': False,
            'use_llvm_cmake_files': False,  # XXX Should these files be used by conan at all?
            'clean_build_bin': True,  # prevent 40gb debug build folder

            # creating job pools with current free memory
            'ram_per_compile_job': '2000',
            'ram_per_link_job': '14000',
        }
    }

    exports = 'patches/**/*'

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def configure(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_zlib
            del self.options.with_xml2
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, '14')

        if self.options.shared:
            self.output.warning(
                "BUILD_SHARED_LIBS is only recommended for use by LLVM developers. If you want to build LLVM as a shared library, you should use the LLVM_BUILD_LLVM_DYLIB option.")

    def validate(self):
        # check keep_binaries_regex early to fail early
        re.compile(str(self.options.keep_binaries_regex))

        # TODO tools.Version ?
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "10":
            raise ConanInvalidConfiguration(
                "Compiler version too low for this package.")

        if is_msvc(self) and tools.Version(self.settings.compiler.version) < "16.4":
            raise ConanInvalidConfiguration(
                "An up to date version of Microsoft Visual Studio 2019 or newer is required.")

        if self.settings.build_type == "Debug" and not self.options.enable_debug:
            raise ConanInvalidConfiguration(
                "Set the 'enable_debug' option to allow debug builds")

        for project in projects:
            for runtime in runtimes:
                if project == runtime and self.options.get_safe('with_project_' + project, False) and self.options.get_safe('with_runtime_' + runtime, False):
                    raise ConanInvalidConfiguration(
                        f"Duplicate entry in enabled projects / runtime found for \"with_project_{project}\"")

    def system_requirements(self):
        # TODO test in different environments
        # TODO is printed during test, is it also checked during consume? Probably that would be an error.
        if self.options["with_runtime_compiler-rt"] and Apt(self).check(["libc6-dev-i386"]):
            raise ConanInvalidConfiguration(
                "For compiler-rt you need the x86 header bits/libc-header-start.h, please install libc6-dev-i386")

    def requirements(self):
        if self.options.with_ffi:
            self.requires('libffi/[>3.4.0 <4.0.0]')
        if self.options.get_safe('with_zlib', False):
            self.requires('zlib/[>1.2.0 <2.0.0]')
        if self.options.get_safe('with_xml2', False):
            self.requires('libxml2/[>2.9.0 <3.0.0]')
        if self.options.get_safe('with_z3', False):
            self.requires('z3/[>4.8.0 <5.0.0]')

    def build_requirements(self):
        # Older cmake versions may have issues generating the graphviz output used
        # to model the components
        self.build_requires("cmake/[>=3.21.3 <4.0.0]")
        self.build_requires("ninja/[>=1.10.0 <2.0.0]")

    def generate(self):
        tc = CMakeToolchain(self, "Ninja")
        tc.generate()

    def build(self):
        cmake = self._cmake_configure()
        cmake.build()

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

        cmake = CMake(self)
        cmake.configure(
            cli_args=['--graphviz=graph/llvm.dot'],
            variables={
                'BUILD_SHARED_LIBS': self.options.shared,
                'LIBOMP_ENABLE_SHARED': self.options.shared,
                # cmake RPATH handling https://gitlab.kitware.com/cmake/community/-/wikis/doc/cmake/RPATH-handling#default-rpath-settings
                # default behaviour for RPATH is to clear it on install
                # skipping RPATH for build affects also RUNPATH but
                # llvm-tblgen with BUILD_SHARED_LIBS needs it during build else build invocation fails because .so not found
                # e.g. readelf -d bin/llvm-tblgen shows RUNPATH $ORIGIN/../lib for build and install location, which is fine in every case.
                # Only if executed with elevated privileges this is ignored because of security concerns (it contains $ORIGIN and isn't absolute).
                # CMAKE_SKIP_RPATH # default is fine, kept for documentation.
                'LLVM_TARGET_ARCH': 'host',
                'LLVM_TARGETS_TO_BUILD': self.options.targets,
                'LLVM_BUILD_LLVM_DYLIB': self.options.llvm_build_llvm_dylib,
                'LLVM_DYLIB_COMPONENTS': self.options.llvm_dylib_components,
                'LLVM_LINK_LLVM_DYLIB': self.options.llvm_link_llvm_dylib,
                # llvm default on
                'LLVM_ENABLE_PIC': self.options.get_safe('fPIC', default=False),
                'LLVM_ABI_BREAKING_CHECKS': 'WITH_ASSERTS',
                'LLVM_ENABLE_WARNINGS': True,
                'LLVM_ENABLE_PEDANTIC': True,
                'LLVM_ENABLE_WERROR': False,
                # from llvm-core:
                # Visual Studio version 16.4, which is known by miscompiling LLVM, is currently being used by conan-center-index's CCI.
                # Let's use LLVM_TEMPORARILY_ALLOW_OLD_TOOLCHAIN to make that compilation pass until Visual Studio is upgraded.
                'LLVM_TEMPORARILY_ALLOW_OLD_TOOLCHAIN': True,
                'LLVM_USE_RELATIVE_PATHS_IN_DEBUG_INFO': False,
                'LLVM_BUILD_INSTRUMENTED_COVERAGE': False,
                'LLVM_OPTIMIZED_TABLEGEN': True,  # NOT default, can speedup compilation a lot
                'LLVM_REVERSE_ITERATION': False,
                'LLVM_ENABLE_BINDINGS': False,  # NOT default, dont build OCaml and go bindings
                'LLVM_CCACHE_BUILD': False,
                'LLVM_INCLUDE_TOOLS': True,
                'LLVM_INCLUDE_EXAMPLES': False,  # NOT default
                'LLVM_BUILD_TESTS': False,
                'LLVM_INCLUDE_TESTS': False,  # NOT default
                'LLVM_INCLUDE_BENCHMARKS': False,
                'LLVM_APPEND_VC_REV': True,
                'LLVM_BUILD_DOCS': False,
                'LLVM_ENABLE_IDE': False,
                # NOT default Use terminfo database if available.
                'LLVM_ENABLE_TERMINFO': False,
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
                'LLVM_USE_SANITIZER': self.options.llvm_use_sanitizer,
                'LLVM_RAM_PER_COMPILE_JOB': self.options.ram_per_compile_job,
                'LLVM_RAM_PER_LINK_JOB': self.options.ram_per_link_job
            },
            build_script_folder=os.path.join(self.source_folder, 'llvm'))
        if is_msvc(self):
            build_type = str(self.settings.build_type).upper()
            cmake.definitions['LLVM_USE_CRT_{}'.format(build_type)] = \
                self.settings.compiler.runtime
        return cmake

    def _is_installed_llvm_lib(self, target_name):
        """Is the given target installed by llvm? Is it a library?"""
        package_lib_folder = os.path.join(self.package_folder, "lib")
        return os.path.exists(os.path.join(package_lib_folder, f"lib{target_name}.a")) or \
            os.path.exists(os.path.join(package_lib_folder, f"lib{target_name}.so")) or \
            os.path.exists(os.path.join(
                package_lib_folder, f"lib{target_name}.dylib"))

    def _package_bin(self):
        """Keep binaries which are matching recipe option keep_binaries_regex.
        Keeps also links in between, removes everything else.
        Returns list of all binaries."""
        bin_matcher = re.compile(str(self.options.keep_binaries_regex))
        keep_binaries = []
        # resolve binaries to keep which are links, so we need to keep link target as well.
        # Binaries are also used to skip targets
        build_bin_path = os.path.join(self.build_folder, 'bin')
        package_bin_path = os.path.join(self.package_folder, 'bin')
        # missed targets by the method below
        binaries = ["lldb-test", "clang-fuzzer", "clang-objc-fuzzer"]
        binaries.extend(os.listdir(build_bin_path))
        binaries.extend(os.listdir(package_bin_path))
        binaries = list(set(binaries))
        binaries.sort()
        for bin in binaries:
            if bin_matcher.match(bin):
                keep_binaries.append(bin)
                current_bin = bin
                # there are links like clang++ -> clang -> clang-14
                while os.path.islink(os.path.join('bin', current_bin)):
                    current_bin = os.path.basename(
                        os.readlink(os.path.join('bin', current_bin)))
                    keep_binaries.append(current_bin)

        # remove unneccessary binaries from package
        for bin in binaries:
            bin_path = os.path.join(package_bin_path, bin)
            if bin in keep_binaries:
                self.output.info(f"Keeping binary \"{bin}\" from package")
            elif os.path.isfile(bin_path) or os.path.islink(bin_path):
                self.output.info(f"Removing binary \"{bin}\" from package")
                os.remove(bin_path)

        return binaries

    def _package_various_removing(self):
        # remove unneccessary files from package
        ignore = ["share", "libexec", "**/Find*.cmake", "**/*Config.cmake"]
        for ignore_entry in ignore:
            ignore_glob = os.path.join(self.package_folder, ignore_entry)

            for ignore_path in glob.glob(ignore_glob, recursive=True):
                self.output.info(
                    'Removing ignored file/directory "{}" from package'.format(ignore_path))

                if os.path.isfile(ignore_path):
                    os.remove(ignore_path)
                else:
                    shutil.rmtree(ignore_path)

        # remove binaries from build, in debug builds these can take 40gb of disk space but are fast to recreate
        if self.options.clean_build_bin:
            rmdir(self, os.path.join(self.build_folder, 'bin'))

    def package(self):
        cmake = self._cmake_configure()
        cmake.install()

        copy(self,
             "LICENSE.TXT",
             src=os.path.join(self.source_folder, "clang"),
             dst="licenses",
             keep_path=False,
             )

        binaries = self._package_bin()
        self._package_various_removing()

        # creating dependency graph
        # from: libA -> libB -> obj... -> libSystem
        # to: libA -> libB, libB -> libSystem
        with chdir(self, 'graph'):
            dot_text = load(self, 'llvm.dot').replace('\r\n', '\n')
        dep_regex = re.compile(r'//\s(.+)\s->\s(.+)$', re.MULTILINE)
        deps = re.findall(dep_regex, dot_text)

        # map dependency names
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
            if not self._is_installed_llvm_lib(target) and target not in external_targets_keys:
                dummy_targets[target].append(dep)
        dummy_targets_keys = dummy_targets.keys()

        # fill components with relevant targets
        # relevant = installed by llvm and is a lib
        components = defaultdict(list)
        ignored_deps = []
        for lib, dep in deps:
            if lib in binaries:
                continue

            if self._is_installed_llvm_lib(lib):
                components[lib]

                if isinstance(dep, list):
                    current_deps = dep
                elif " " in dep:
                    current_deps = dep.split()  # lib: omp dep: str(-lpthread -lrt)
                else:
                    current_deps = [dep]

                visited = components[lib].copy()
                while len(current_deps) > 0:
                    current_dep = current_deps.pop()
                    visited.append(current_dep)

                    if current_dep in binaries:
                        continue
                    elif self._is_installed_llvm_lib(current_dep):
                        components[current_dep]

                    # Copied from llvm-core but not used on linux, maybe for other systems? ==>
                    elif current_dep.startswith('-delayload:'):
                        continue

                    elif os.path.exists(current_dep):
                        current_dep = os.path.splitext(
                            os.path.basename(current_dep))[0]
                        current_dep = current_dep.replace('lib', '')
                    # <==

                    # e.g. -lpthread -> pthread
                    if current_dep.startswith("-l"):
                        current_dep = current_dep[2:]

                    if current_dep in dummy_targets_keys:
                        for d in dummy_targets[current_dep]:
                            if not visited:
                                current_deps.append(d)
                    elif self._is_installed_llvm_lib(current_dep):
                        if not self.options.shared:
                            components[lib].append(current_dep)
                    elif current_dep in external_targets_keys:
                        components[lib].append(external_targets[current_dep])
                    else:
                        ignored_deps.append(current_dep)
                components[lib] = list(set(components[lib]))
                if lib in components[lib]:
                    raise ConanException(
                        f"Conan recipe error, found circular dependency for {lib} over {dep}")
        ignored_deps = list(set(ignored_deps))
        self.output.info(
            f'ignored these dependencies, will not propagate these to conan: {ignored_deps}')

        # workaround for circular dependencies which will create errors in conan
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

        # remove circular dependencies in components
        for target, remove in remove_dependencies:
            if target in keys:
                if remove in components[target]:
                    components[target].remove(remove)
                if target in components[remove]:
                    components[remove].remove(target)
        found_circular_dep = False
        for c in keys:
            for c_dep in components[c]:
                if c_dep in keys:
                    if c in components[c_dep]:
                        self.output.error(
                            f"circular dependency found: {c} -> {c_dep} -> {c}")
                        found_circular_dep = True
        if found_circular_dep:
            raise ConanException(
                f"circular dependency found, see error log above")

        # manually fix some dependencies
        if not self.options.shared:
            if self.options.get_safe('with_zlib', False):
                if not 'z' in components['LLVMSupport']:
                    components['LLVMSupport'].append('z')

            # fix: ERROR: llvm/14.0.6@...: Required package 'libxml2' not in component 'requires'
            # llvm 14.0.6 searched for LibXml2::LibXml2
            xml2_linking = ["LLVMWindowsManifest", "lldbHost", "c-index-test"]
            report_xml2_issue = self.options.with_xml2
            if self.options.with_xml2:
                for component in xml2_linking:
                    if component in components:
                        self.cpp_info.components[component].requires.append(
                            "libxml2::libxml2")
                        report_xml2_issue = False
            if report_xml2_issue:
                raise "Recipe issue in llvm/*:with_xml2=True is set but no component requires it, this will only error if consumed."

        # write components.json for package_info
        components_path = os.path.join(
            self.package_folder, 'lib', 'components.json')
        with open(components_path, 'w') as components_file:
            json.dump(components, components_file, indent=4)

    def package_id(self):
        del self.info.options.enable_debug
        del self.info.options.use_llvm_cmake_files
        del self.info.options.clean_build_bin
        del self.info.options.ram_per_compile_job
        del self.info.options.ram_per_link_job

    def package_info(self):
        module_subfolder = os.path.join("lib", "cmake")
        self.cpp_info.set_property("cmake_file_name", "LLVM")

        if self.options.shared:
            self.cpp_info.libs = collect_libs(self)
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
            self.cpp_info.components[component].requires.extend(
                dep for dep in deps if self._is_installed_llvm_lib(dep))

            for lib, target in external_targets.items():
                if lib in deps:
                    self.cpp_info.components[component].requires.append(target)

            self.cpp_info.components[component].system_libs = [
                dep for dep in deps
                if not self._is_installed_llvm_lib(dep) and dep not in dependencies
            ]

            self.cpp_info.components[component].set_property(
                "cmake_target_name", component)
            self.cpp_info.components[component].builddirs.append(
                module_subfolder)
            self.cpp_info.components[component].names["cmake_find_package"] = component
            self.cpp_info.components[component].names["cmake_find_package_multi"] = component

            if self.options.use_llvm_cmake_files:
                self.cpp_info.components[component].build_modules["cmake_find_package"].append(
                    os.path.join(module_subfolder,
                                 "LLVMConfigInternal.cmake")
                )
                self.cpp_info.components[component].build_modules["cmake_find_package_multi"].append(
                    os.path.join(module_subfolder,
                                 "LLVMConfigInternal.cmake")
                )
