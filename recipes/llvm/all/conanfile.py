from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get, apply_conandata_patches, chdir, load, copy
from conan.tools.microsoft import is_msvc
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
from collections import defaultdict
from conan.errors import ConanException
from conan.tools.scm import Version
from pathlib import Path
import os
import shutil
import glob
import re
import json

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
    # 'clang',
    # 'clang-tools-extra',
    # 'libc', # clang-14/15 crashes in {sin,cos,tan} for llvm-{13.0.0,14.0.6} in debug, clang-15 release looks fine
    # 'libclc',
    # 'lld',
    # 'lldb',
    # 'openmp',
    # 'polly',
    # 'pstl',
]
default_runtimes = [
    # 'compiler-rt',
    # 'libc',
    # 'libcxx',
    # 'libcxxabi',
    # 'libunwind',
]


class Llvm(ConanFile):
    name = 'llvm'
    description = 'The LLVM Project is a collection of modular and reusable compiler and toolchain technologies'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://github.com/llvm/llvm-project'
    license = 'Apache-2.0'
    topics = 'cpp', 'compiler', 'tooling', 'clang'

    settings = 'os', 'arch', 'compiler', 'build_type'

    # dont copy source to build directory, large software opt
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
            'with_curl': [True, False],
            'with_zstd': [True, False],
            'with_httplib': [True, False],
            'keep_binaries_regex': ['ANY'],

            # options removed in package id
            'use_llvm_cmake_files': [True, False],
            'ram_per_compile_job': ['ANY'],
            'ram_per_link_job': ['ANY'],
            # conan center index ci workaround, memory consumption to high in debug builds
            # and only latest versions are enabled in ci to reduce ci runtime by days
            'conan_center_index_limits': [True, False],
            'enable_unsafe_mode': [True, False],
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
            # TODO curl 7.76.0 check is failing in config-ix.cmake
            'with_curl': False,
            'with_zstd': True,
            'with_httplib': False,
            # TODO default True, issues with liblldb.so and conan: Findlibxml2.cmake not provided
            'with_xml2': False,
            'keep_binaries_regex': '^$',

            # options removed in package id
            # XXX Should these files used by conan at all?
            'use_llvm_cmake_files': False,
            # creating job pools with current free memory
            'ram_per_compile_job': '2000',
            'ram_per_link_job': '14000',
            'conan_center_index_limits': True,
            'enable_unsafe_mode': False,
        }
    }

    exports_sources = 'patches/**/*', 'conandata.yml'

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def is_windows(self):
        return self.settings.os == "Windows"

    def is_macos(self):
        return self.settings.os == "MacOS"

    def is_linux(self):
        return self.settings.os == "Linux"

    # checking options before requirements are build
    def configure(self):
        if self.is_windows():
            self.options.rm_safe("fPIC")  # FPIC MANAGEMENT (KB-H007)

        if self.options.shared:
            self.options.rm_safe("fPIC")  # FPIC MANAGEMENT (KB-H007)
            self.output.warning(
                "BUILD_SHARED_LIBS is only recommended for use by LLVM developers. If you want to build LLVM as a shared library, you should use the LLVM_BUILD_LLVM_DYLIB option.")

        release = Version(self.version).major
        unsupported_options = []
        if release < 14:
            unsupported_options.append('with_curl')
        if release < 15:
            unsupported_options.append('with_zstd')
            unsupported_options.append('with_httplib')
        # TODO fix with_zstd and llvm 17
        if release >= 17:
            self.output.warning(f"with_zstd will fail in llvm 17 with conan 2")
            unsupported_options.append('with_zstd')
        for opt in unsupported_options:
            self.output.warning(f"{opt} is unsupported in llvm {release}")
            self.options.rm_safe(opt)

    def validate(self):
        if self.is_windows():
            if self.options.shared:
                raise ConanInvalidConfiguration(
                    "BUILD_SHARED_LIBS options is not supported on Windows.")
            if is_msvc(self):
                if self.options.llvm_build_llvm_dylib:
                    raise ConanInvalidConfiguration(
                        "Generating libLLVM is not supported on MSVC"
                    )

        try:
            re.compile(str(self.options.keep_binaries_regex))
        except re.error as e:
            self.output.error(f"re.error: {e.msg}")
            raise ConanInvalidConfiguration(
                "Option keep_binaries_regex isn't a valid pattern")

        if self.settings.compiler.cppstd:
            ver = Version(self.version).major
            if ver < 16:
                check_min_cppstd(self, '14')
            elif ver >= 16:
                check_min_cppstd(self, '17')

        for project in projects:
            for runtime in runtimes:
                if project == runtime and self.options.get_safe('with_project_' + project, False) and self.options.get_safe('with_runtime_' + runtime, False):
                    raise ConanInvalidConfiguration(
                        f"Duplicate entry in enabled projects / runtime found for \"with_project_{project}\"")

        if self.options.shared:
            if self.options.llvm_build_llvm_dylib:
                raise ConanInvalidConfiguration(
                    "LLVM needs static compilation for dylib.")
        elif self.options.llvm_link_llvm_dylib and not self.options.llvm_build_llvm_dylib:
            raise ConanInvalidConfiguration(
                "You can't link against dylib if you don't build dylib. Please also set llvm_build_llvm_dylib=True")

        if self.options.conan_center_index_limits:
            # XXX conandata.yml is reduced in cci ci to exactly one version so we can't look it up
            # 14 needed for a follow up pr, 16 and 17 are identical in requirements
            if not str(self.version) in ['14.0.6', '17.0.2']:
                raise ConanInvalidConfiguration(
                    "llvm version is disabled for conan center index ci. We have a tight ci budget for such a huge recipe. You can enable it with option conan_center_index_limits=False.")
            if self.settings.build_type == "Debug":
                raise ConanInvalidConfiguration(
                    "LLVM Debug builds are disabled as a workaround of conan center index ci memory limits. You can enable it with option conan_center_index_limits=False.")
            if self.options.shared:
                raise ConanInvalidConfiguration(
                    "Shared builds are disabled for cci ci for max total build time reasons. You can enable it with option conan_center_index_limits=False.")
            if self.is_linux():
                if self.settings.compiler == "clang" and self.settings.compiler.version != "12":
                    raise ConanInvalidConfiguration(
                        "Compiler is excluded from cci ci to reduce ci time. You can enable it with option conan_center_index_limits=False.")
                if self.settings.compiler == "gcc" and self.settings.compiler.version != "10":
                    raise ConanInvalidConfiguration(
                        "Compiler is excluded from cci ci to reduce ci time. You can enable it with option conan_center_index_limits=False.")

        if not self.options.enable_unsafe_mode:
            if self.settings.compiler == "gcc":
                if Version(self.settings.compiler.version) < Version("10"):
                    raise ConanInvalidConfiguration(
                        "Compiler version too low for this package. If you want to try it set enable_unsafe_mode=True")
            elif self.settings.compiler == "clang":
                if self.is_linux() and self.settings.compiler.libcxx in ['libc++']:
                    # libc++ compiles but test linkage fails
                    raise ConanInvalidConfiguration(
                        "Configured compiler.libcxx=libc++ will fail in test_package linking. If you want to try it set enable_unsafe_mode=True")
            elif is_msvc(self):
                # TODO probably migration needed: https://github.com/conan-io/tribe/blob/main/design/032-msvc_support.md
                if Version(self.settings.compiler.version) < Version("16.4"):
                    raise ConanInvalidConfiguration(
                        "An up to date version of Microsoft Visual Studio 2019 or newer is required. If you want to try it set enable_unsafe_mode=True")

    # XXX Still unsure if we should even check for this at all, errors like this would need a lot of fine tuning for each environment to be correct.
    # import for Apt doesn't satisfy: E9011(conan-import-tools)
    # def system_requirements(self):
        # if self.is_linux():
        #     # from conan.tools.system.package_manager import Apt
        #     if self.options.get_safe('with_runtime_compiler-rt', False):
        #         # apt should work for ubuntu/debian if apt is not installed this is skipped
        #         if Apt(self).check(["libc6-dev-i386"]):
        #             raise ConanInvalidConfiguration(
        #                 "For compiler-rt you need the x86 header bits/libc-header-start.h, please install libc6-dev-i386")

    def requirements(self):
        if self.options.with_ffi:
            # no version requirement in llvm 13-17
            self.requires('libffi/[>3.4.0 <4.0.0]')
        if self.options.get_safe('with_zlib', False):
            # no version requirement in llvm 13-17
            self.requires('zlib/[>1.2.0 <2.0.0]')
        if self.options.get_safe('with_xml2', False):
            # min version requirement from llvm 13-17
            self.requires('libxml2/[>=2.5.3 <3.0.0]')
        if self.options.get_safe('with_z3', False):
            # min version requirement from llvm 13-17
            self.requires('z3/[>=4.7.1 <5.0.0]')
        if self.options.get_safe('with_curl', False):
            # no version requirement in llvm 14-17
            self.requires('libcurl/[>=7.76.0 <9.0.0]')
        if self.options.get_safe('with_zstd', False):
            # no version number in llvm 15-17
            self.requires('zstd/[>=1.3.5 <2.0.0]')
        if self.options.get_safe('with_httplib', False):
            # no version number in llvm 15-17
            self.requires('cpp-httplib/[>=0.5.4 <1.0.0]')

    def build_requirements(self):
        # Older cmake versions may have issues generating the graphviz output used
        # to model the components
        self.tool_requires("cmake/[>=3.21.3 <4.0.0]")
        self.tool_requires("ninja/[>=1.10.0 <2.0.0]")

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

        is_zstd_static = False
        if self.options.get_safe('with_zstd', False):
            is_zstd_static = not self.dependencies["zstd"].options.shared

        cmake = CMake(self)
        # https://releases.llvm.org/13.0.0/docs/CMake.html
        # https://releases.llvm.org/14.0.0/docs/CMake.html
        # https://releases.llvm.org/15.0.0/docs/CMake.html
        # https://releases.llvm.org/16.0.0/docs/CMake.html
        # https://llvm.org/docs/CMake.html#frequently-used-llvm-related-variables
        cmake_definitions = {
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
            # llvm default on, if set to False: lib/libLLVMTableGenGlobalISel.so recompile with -fPIC
            'LLVM_ENABLE_PIC': self.options.get_safe('fPIC', default=True),
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
            'LLVM_Z3_INSTALL_DIR': Path(self.dependencies["z3"].package_folder).resolve().as_posix() if self.options.with_z3 else "",
            'LLVM_ENABLE_LIBPFM': False,
            'LLVM_ENABLE_LIBEDIT': False,
            'LLVM_ENABLE_FFI': self.options.with_ffi,
            # FORCE_ON adds required to find_package
            'LLVM_ENABLE_ZLIB': 'FORCE_ON' if self.options.get_safe('with_zlib', False) else False,
            'LLVM_ENABLE_LIBXML2': 'FORCE_ON' if self.options.get_safe('with_xml2', False) else False,
            'LLVM_ENABLE_CURL': 'FORCE_ON' if self.options.get_safe('with_curl', False) else False,
            'LLVM_ENABLE_ZSTD': 'FORCE_ON' if self.options.get_safe('with_zstd', False) else False,
            'LLVM_USE_STATIC_ZSTD': is_zstd_static,
            'LLVM_ENABLE_HTTPLIB': 'FORCE_ON' if self.options.get_safe('with_httplib', False) else False,
            'LLVM_ENABLE_PROJECTS': ';'.join(enabled_projects),
            'LLVM_ENABLE_RUNTIMES': ';'.join(enabled_runtimes),
            'LLVM_USE_SANITIZER': self.options.llvm_use_sanitizer,
            'LLVM_RAM_PER_COMPILE_JOB': self.options.ram_per_compile_job,
            'LLVM_RAM_PER_LINK_JOB': self.options.ram_per_link_job
        }
        if is_msvc(self):
            build_type = str(self.settings.build_type).upper()
            runtime = str(self.settings.compiler.runtime)
            if not runtime in ['MD', 'MT', 'MTd', 'MDd']:
                runtime_type = str(self.settings.compiler.runtime_type)
                if runtime_type == "Debug" and runtime == "static":
                    runtime = 'MTd'
                elif runtime_type == "Debug" and runtime == "dynamic":
                    runtime = 'MTd'
                elif runtime_type == "Release" and runtime == "static":
                    runtime = 'MT'
                elif runtime_type == "Release" and runtime == "dynamic":
                    runtime = 'MD'
            cmake_definitions.update(
                {
                    # will be replaced in llvm 18 by CMAKE_MSVC_RUNTIME_LIBRARY
                    # llvm expects: MD, MT, MTd, MDd
                    f"LLVM_USE_CRT_{build_type}": runtime
                }
            )
        # Conan Center Index CI optimization, in build_type=Debug the CI is killing it because of high memory usage:
        # quote: This option reduces link-time memory usage by reducing the amount of debug information that the linker needs to resolve.
        # It is recommended for platforms using the ELF object format, like Linux systems when linker memory usage is too high.
        is_platform_ELF_based = self.settings.os in [
            'Linux', 'Android', 'FreeBSD', 'SunOS', 'AIX', 'Neutrino', 'VxWorks'
        ]
        if is_platform_ELF_based:
            self.output.info(
                f"your platform \"{self.settings.os}\" is using the ELF format, optimizing memory usage during debug build linking.")
            cmake_definitions.update(
                {
                    'LLVM_USE_SPLIT_DWARF': True
                }
            )
        cmake.configure(
            cli_args=['--graphviz=graph/llvm.dot'],
            variables=cmake_definitions,
            build_script_folder=os.path.join(self.source_folder, 'llvm'))

        return cmake

    def _is_installed_llvm_lib(self, target_name):
        """Is the given target installed by llvm? Is it a library?"""
        package_lib_folder = os.path.join(self.package_folder, "lib")
        return os.path.exists(os.path.join(package_lib_folder, f"lib{target_name}.a")) or \
            os.path.exists(os.path.join(package_lib_folder, f"lib{target_name}.so")) or \
            os.path.exists(os.path.join(
                package_lib_folder, f"lib{target_name}.dylib"))

    def _is_shared_llvm_lib(self, target_name):
        """Depending on llvm configuration there are static and shared libraries, so options.shared isn't correct."""
        package_lib_folder = os.path.join(self.package_folder, "lib")
        return os.path.exists(os.path.join(package_lib_folder, f"lib{target_name}.so")) or \
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

    def package(self):
        cmake = self._cmake_configure()
        cmake.install()

        copy(self,
             "LICENSE.TXT",
             src=os.path.join(self.source_folder, "clang"),
             dst=os.path.join(self.package_folder, "licenses"),
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
            'libxml2::libxml2': 'xml2',
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
                        # Because .a and .so are mixed for specific llvm configuration, check if the file is actually shared
                        # shared files contain their internal dependencies in elf header, we dont need to handle them
                        if not self._is_shared_llvm_lib(current_dep):
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

        # .so already containing .a, so clear deps of e.g. LLVM.so which are installed by LLVM itself
        # every component which is in is available = installed
        for shared_component in components:
            if self._is_shared_llvm_lib(shared_component):
                external_dependencies = []
                for dep in components[shared_component]:
                    if not self._is_installed_llvm_lib(current_dep):
                        external_dependencies.append(dep)
                components[shared_component] = external_dependencies

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
        if self.options.get_safe('with_zlib', False):
            if not 'z' in components['LLVMSupport']:
                components['LLVMSupport'].append('z')

        # fix: ERROR: llvm/14.0.6@...: Required package 'libxml2' not in component 'requires'
        xml2_linking = ["LLVMWindowsManifest", "lldbHost", "c-index-test"]
        report_xml2_issue = self.options.with_xml2
        if self.options.with_xml2:
            for component in xml2_linking:
                if component in components:
                    components[component].append(
                        "xml2")
                    self.output.info(
                        f"forced dependency to \"xml2\" for target {component}")
                    report_xml2_issue = False

            # XXX could be an issue in libxml2 recipe?
            # ld: error: undefined symbol: libiconv_open, libiconv_close, libiconv in libxml2_la-encoding
            component = "lldbHost"
            if component in components:
                components[component].append("iconv")
                self.output.info(
                    f"forced dependency to \"iconv\" for target {component}")
        if report_xml2_issue:
            raise ConanException(
                "Recipe issue in llvm/*:with_xml2=True is set but no component requires it, this will only error if consumed.")

        # write components.json for package_info
        components_path = os.path.join(
            self.package_folder, 'lib', 'components.json')
        with open(components_path, 'w') as components_file:
            json.dump(components, components_file, indent=4)

    def package_id(self):
        del self.info.options.use_llvm_cmake_files
        del self.info.options.ram_per_compile_job
        del self.info.options.ram_per_link_job
        del self.info.options.conan_center_index_limits
        del self.info.options.enable_unsafe_mode

    def package_info(self):
        module_subfolder = os.path.join("lib", "cmake")
        self.cpp_info.set_property("cmake_file_name", "LLVM")

        components_path = \
            os.path.join(self.package_folder, 'lib', 'components.json')
        with open(components_path, 'r') as components_file:
            components = json.load(components_file)

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
                if not self._is_installed_llvm_lib(dep) and dep not in external_targets.keys()
            ]

            self.cpp_info.components[component].set_property(
                "cmake_target_name", component)
            self.cpp_info.components[component].builddirs.append(
                module_subfolder)
            self.cpp_info.components[component].set_property(
                "cmake_find_package", component)
            self.cpp_info.components[component].set_property(
                "cmake_find_package_multi", component)

            if self.options.use_llvm_cmake_files:
                self.cpp_info.components[component].build_modules["cmake_find_package"].append(
                    os.path.join(module_subfolder,
                                 "LLVMConfigInternal.cmake")
                )
                self.cpp_info.components[component].build_modules["cmake_find_package_multi"].append(
                    os.path.join(module_subfolder,
                                 "LLVMConfigInternal.cmake")
                )

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "LLVM"
        self.cpp_info.names["cmake_find_package_multi"] = "LLVM"
