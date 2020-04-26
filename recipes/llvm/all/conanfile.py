from conans import ConanFile, tools, CMake
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration
import os, shutil

projects = [
    'clang',
    'clang-tools-extra',
    'compiler-rt',
    'debuginfo-tests',
    'libc',
    'libclc',
    'libcxx',
    'libcxxabi',
    'libunwind',
    'lld',
    'lldb',
    'mlir',
    'openmp',
    'parallel-libs',
    'polly',
    'pstl'
]

default_projects = [
    'clang',
    'compiler-rt'
]

class Llvm(ConanFile):
    name = 'llvm'
    description = 'The LLVM Project is a collection of modular and reusable compiler and toolchain technologies'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://github.com/llvm/llvm-project'
    license = 'Apache 2.0'
    topics = 'conan', 'c++', 'compiler', 'tooling'

    settings = 'os', 'arch', 'compiler', 'build_type'

    no_copy_source = True
    _source_subfolder = 'source_subfolder'

    options = {**{ 'with_' + project : [True, False] for project in projects }, **{
        'fPIC': [True, False]
    }}
    default_options = {**{ 'with_' + project : project in default_projects for project in projects }, **{
        'fPIC': True
    }}
    generators = 'cmake_find_package'

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = 'llvm-project-llvmorg-' + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, '14')

        if self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) < "19.1":
            raise ConanInvalidConfiguration("Need MSVC >= 19.1")

    def build(self):
        enabled_projects = [project for project in projects if getattr(self.options, 'with_' + project)]
        self.output.info('Enabled LLVM subprojects: {}'.format(', '.join(enabled_projects)))

        cmake = CMake(self);
        cmake.configure(
            defs = {
                'LLVM_ENABLE_PROJECTS': ';'.join(enabled_projects)
            },
            source_folder = os.path.join(self._source_subfolder, 'llvm')
        )
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        self.copy('LICENSE.TXT', src='clang', dst='licenses', keep_path=False)

        directories_to_ignore = [
            'share'
        ]

        for ignore_dir in directories_to_ignore:
            shutil.rmtree(os.path.join(self.package_folder, ignore_dir))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.builddirs = ['lib/cmake']
