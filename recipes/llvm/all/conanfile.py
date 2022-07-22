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
]
default_runtimes = [
    #'libcxx',
    # libcxxabi appears to be required to build libcxx.
    # See: https://reviews.llvm.org/D63883
    #'libcxxabi',
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
            'with_ffi': [True, False],
            'with_zlib': [True, False],
            'with_xml2': [True, False],
            'use_llvm_cmake_files': [True, False],
            'enable_debug': [True, False],
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
            'enable_debug': False,
            'use_llvm_cmake_files': False,
        }
    }
    generators = 'cmake_find_package'

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
        self.build_requires("cmake/3.21.3")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, '14')

    def _patch_sources(self):
        for patch in self.conan_data.get('patches', {}).get(self.version, []):
            tools.patch(**patch)

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
        cmake.configure(defs={
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
            'LLVM_OPTIMIZED_TABLEGEN': True,
            'LLVM_REVERSE_ITERATION': False,
            'LLVM_ENABLE_BINDINGS': False,
            'LLVM_CCACHE_BUILD': False,
            'LLVM_INCLUDE_TOOLS': self.options.shared,
            'LLVM_INCLUDE_EXAMPLES': False,
            'LLVM_INCLUDE_TESTS': False,
            'LLVM_INCLUDE_BENCHMARKS': False,
            'LLVM_APPEND_VC_REV': False,
            'LLVM_BUILD_DOCS': False,
            'LLVM_ENABLE_IDE': False,
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
            'LLVM_ENABLE_Z3_SOLVER': False,
            'LLVM_ENABLE_LIBPFM': False,
            'LLVM_ENABLE_LIBEDIT': False,
            'LLVM_ENABLE_FFI': self.options.with_ffi,
            'LLVM_ENABLE_ZLIB': self.options.get_safe('with_zlib', False),
            'LLVM_ENABLE_LIBXML2': self.options.get_safe('with_xml2', False),
            'LLVM_ENABLE_PROJECTS': ';'.join(enabled_projects),
            'LLVM_ENABLE_RUNTIMES': ';'.join(enabled_runtimes),
            'LLVM_ENABLE_BINDINGS': False,
            'LLVM_ENABLE_RTTI': self.options.rtti,
        },
                        source_folder=os.path.join(self._source_subfolder,
                                                   'llvm'))
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

    def package(self):
        cmake = self._cmake_configure()
        cmake.install()

        self.copy(
            "LICENSE.TXT",
            src=os.path.join(self._source_subfolder, "clang"),
            dst="licenses",
            keep_path=False,
        )

        ignore = ["share", "libexec", "**/Find*.cmake", "**/*Config.cmake"]

        for ignore_entry in ignore:
            ignore_glob = os.path.join(self.package_folder, ignore_entry)

            for ignore_path in glob.glob(ignore_glob, recursive=True):
                self.output.info(
                    'Remove ignored file/directory "{}" from package'.format(
                        ignore_path
                    )
                )

                if os.path.isfile(ignore_path):
                    os.remove(ignore_path)
                else:
                    shutil.rmtree(ignore_path)

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

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.builddirs = ["lib/cmake"]
