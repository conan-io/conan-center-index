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
    'libcxx',
]

default_projects = ['clang', 'compiler-rt']


class Llvm(ConanFile):
    name = 'llvm'
    description = 'The LLVM Project is a collection of modular and reusable compiler and toolchain technologies'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://github.com/llvm/llvm-project'
    license = 'Apache-2.0'
    topics = 'cpp', 'compiler', 'tooling', 'clang'

    settings = 'os', 'arch', 'compiler', 'build_type'

    no_copy_source = True
    _source_subfolder = 'source_subfolder'

    options = {
        **{'with_project_' + project: [True, False]
           for project in projects},
        **{"with_runtime_" + runtime: [True, False]
           for runtime in runtimes},
        **{
            'fPIC': [True, False],
            'rtti': [True, False],
            'enable_debug': [True, False]
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
            'fPIC': True,
            'rtti': True,
            'enable_debug': False,
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

    def build_requirements(self):
        self.build_requires("cmake/3.21.3")

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, '14')

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

        cmake = CMake(self, parallel=False)
        cmake.configure(defs={
            'LLVM_ENABLE_PROJECTS': ';'.join(enabled_projects),
            'LLVM_ENABLE_RUNTIMES': ';'.join(enabled_runtimes),
            'LLVM_ENABLE_BINDINGS': False,
            'LLVM_ENABLE_RTTI': self.options.rtti,
        },
                        source_folder=os.path.join(self._source_subfolder,
                                                   'llvm'))
        return cmake

    def build(self):
        cmake = self._cmake_configure()
        cmake.build()

    def package(self):
        cmake = self._cmake_configure()
        cmake.install()

        self.copy('LICENSE.TXT',
                  src=self.project_folder('clang'),
                  dst='licenses',
                  keep_path=False)

        ignore = ['share', 'libexec', '**/Find*.cmake', '**/*Config.cmake']

        for ignore_entry in ignore:
            ignore_glob = os.path.join(self.package_folder, ignore_entry)

            for ignore_path in glob.glob(ignore_glob, recursive=True):
                self.output.info(
                    'Remove ignored file/directory "{}" from package'.format(
                        ignore_path))

                if os.path.isfile(ignore_path):
                    os.remove(ignore_path)
                else:
                    shutil.rmtree(ignore_path)

    def validate(self):
        if self.settings.compiler == "gcc" and tools.Version(
                self.settings.compiler.version) < "10":
            raise ConanInvalidConfiguration(
                "Compiler version too low for this package.")

        if self.settings.compiler == "Visual Studio" and Version(
                self.settings.compiler.version) < "16.4":
            raise ConanInvalidConfiguration(
                "An up to date version of Microsoft Visual Studio 2019 or newer is required."
            )

        if self.settings.build_type == "Debug" and not self.options.enable_debug:
            raise ConanInvalidConfiguration(
                "Set the 'enable_debug' option to allow debug builds")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.builddirs = ['lib/cmake']
