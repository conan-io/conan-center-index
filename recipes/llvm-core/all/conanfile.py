from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, get, rmdir, save, copy, export_conandata_patches
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

from glob import iglob
import json
import os
from pathlib import Path
import re

required_conan_version = ">=1.62.0"


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

    settings = 'os', 'arch', 'compiler', 'build_type'
    options = {
        'shared': [True, False],
        'fPIC': [True, False],
        'components': ['ANY'],
        'targets': ['ANY'],
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
        'with_terminfo': [True, False],
        'with_zlib': [True, False],
        'with_xml2': [True, False],
        'with_z3': [True, False],
        'use_llvm_cmake_files': [True, False],
        'ram_per_compile_job': ['ANY'],
        'ram_per_link_job': ['ANY'],
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
        'with_terminfo': False, # differs from LLVM default
        'with_xml2': True,
        'with_z3': True,
        'with_zlib': True,
        'use_llvm_cmake_files': False,
        # creating job pools with current free memory
        'ram_per_compile_job': '2000',
        'ram_per_link_job': '14000'
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_ffi:
            self.requires('libffi/3.4.4')
        if self.options.with_zlib:
            self.requires('zlib/1.3.1')
        if self.options.with_xml2:
            self.requires('libxml2/2.12.4')
        self.requires('z3/4.12.4')

    @property
    def _is_gcc(self):
        return self.settings.compiler == "gcc"

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if self._is_gcc and Version(self.settings.compiler.version) >= "13":
            raise ConanInvalidConfiguration(
                f"GCC {self.settings.compiler.version} cannot compile LLVM {self.version}"
            )

        if self._is_windows:
            if self.options.shared:  # Shared builds disabled just due to the CI
                raise ConanInvalidConfiguration('Shared builds not currently supported on Windows')

        if self.options.exceptions and not self.options.rtti:
            raise ConanInvalidConfiguration('Cannot enable exceptions without rtti support')

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # https://releases.llvm.org/12.0.0/docs/CMake.html
        # https://releases.llvm.org/13.0.0/docs/CMake.html
        cmake_definitions = {
            'LLVM_TARGETS_TO_BUILD': self.options.targets,
            'LLVM_BUILD_LLVM_DYLIB': self.options.shared,
            'LLVM_LINK_LLVM_DYLIB': self.options.shared,
            'LLVM_DYLIB_COMPONENTS': self.options.components,
            'LLVM_ABI_BREAKING_CHECKS': 'WITH_ASSERTS',
            'LLVM_INCLUDE_TOOLS': True,
            'LLVM_INCLUDE_EXAMPLES': False,
            'LLVM_INCLUDE_TESTS': False,
            'LLVM_ENABLE_IDE': False,
            'LLVM_ENABLE_EH': self.options.exceptions,
            'LLVM_ENABLE_RTTI': self.options.rtti,
            'LLVM_ENABLE_THREADS': self.options.threads,
            'LLVM_ENABLE_LTO': self.options.lto,
            'LLVM_STATIC_LINK_CXX_STDLIB': self.options.static_stdlib,
            'LLVM_ENABLE_UNWIND_TABLES': self.options.unwind_tables,
            'LLVM_ENABLE_EXPENSIVE_CHECKS': self.options.expensive_checks,
            'LLVM_ENABLE_ASSERTIONS': self.settings.build_type,
            'LLVM_USE_PERF': self.options.use_perf,
            'LLVM_ENABLE_Z3_SOLVER': self.options.with_z3,
            'LLVM_ENABLE_FFI': self.options.with_ffi,
            'LLVM_ENABLE_ZLIB': "FORCE_ON" if self.options.with_zlib else False,
            'LLVM_ENABLE_LIBXML2': "FORCE_ON" if self.options.with_xml2 else False,
            'LLVM_ENABLE_TERMINFO': self.options.with_terminfo,
            'LLVM_RAM_PER_COMPILE_JOB': self.options.ram_per_compile_job,
            'LLVM_RAM_PER_LINK_JOB': self.options.ram_per_link_job
        }
        if is_msvc(self):
            build_type = str(self.settings.build_type).upper()
            cmake_definitions['LLVM_USE_CRT_{}'.format(build_type)] = self.settings.compiler.runtime

        if not self.options.shared:
            cmake_definitions.update({
                'DISABLE_LLVM_LINK_LLVM_DYLIB': True,
                'LLVM_ENABLE_PIC': self.options.get_safe('fPIC', default=False)
            })

        if self.options.use_sanitizer == 'None':
            cmake_definitions['LLVM_USE_SANITIZER'] = ''
        else:
            cmake_definitions['LLVM_USE_SANITIZER'] = self.options.use_sanitizer

        tc.variables.update(cmake_definitions)
        tc.cache_variables.update({
            'CMAKE_TRY_COMPILE_CONFIGURATION': str(self.settings.build_type),
            'BUILD_SHARED_LIBS': False,  # This variable causes LLVM to build shared libs for each separate component,
            # which is probably not what the user wants. Use `LLVM_BUILD_LLVM_DYLIB` instead
            # to build a single shared library
        })
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        graphviz_settings = """
set(GRAPHVIZ_EXECUTABLES OFF)
set(GRAPHVIZ_INTERFACE_LIBS OFF)
set(GRAPHVIZ_OBJECT_LIBS OFF)
        """
        save(self, Path(self.build_folder) / "CMakeGraphVizOptions.cmake", graphviz_settings)
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(cli_args=["--graphviz=graph/llvm.dot"])
        cmake.build()

    @property
    def _is_windows(self):
        return self.settings.os == 'Windows'

    def _llvm_components(self):
        # TODO (@planetmarshall) this is a bit hacky. CMake already has this information, just
        #  parse the LLVM CMake files.
        # The definitive list of built targets is provided by running `llvm-config --components`
        non_distributed = {
            "exegesis"
        }
        graphviz_folder = Path(self.build_folder) / "graph"
        match_component = re.compile(r"""^llvm.dot.LLVM(.+)\.dependers$""")
        for lib in iglob(str(graphviz_folder / '*')):
            if os.path.isdir(lib) or os.path.islink(lib):
                continue
            lib_name = os.path.basename(lib)
            match = match_component.match(lib_name)
            if match:
                component = match.group(1)
                component_name = component.lower()
                if component_name not in non_distributed:
                    yield component.lower(), f"LLVM{component}"

    @property
    def _components_data_file(self):
        return Path(self.package_folder) / "components.json"

    def _write_components(self):
        component_dict = {
            component: lib_name for component, lib_name in self._llvm_components()
        }
        with open(self._components_data_file, 'w') as fp:
            json.dump(component_dict, fp)

    def _read_components(self) -> dict:
        with open(self._components_data_file) as fp:
            return json.load(fp)

    def package(self):
        copy(self, "LICENSE.TXT", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        package_folder = Path(self.package_folder)
        rmdir(self, package_folder / "lib" / "cmake")

        if not self.options.shared:
            self._write_components()

    def package_id(self):
        del self.info.options.use_llvm_cmake_files
        del self.info.options.ram_per_compile_job
        del self.info.options.ram_per_link_job

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "LLVM")

        dependencies = [
            "zlib::zlib",
            "libxml2::libxml2",
            "z3::z3"
        ]

        if not self.options.shared:
            components = self._read_components()

            for component_name, lib_name in components.items():
                self.cpp_info.components[component_name].set_property("cmake_target_name", lib_name)
                self.cpp_info.components[component_name].libs = [lib_name]
                self.cpp_info.components[component_name].requires = dependencies

        else:
            self.cpp_info.set_property("cmake_target_name", "LLVM")
            self.cpp_info.libs = collect_libs(self)
