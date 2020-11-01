from conans import ConanFile, CMake, tools

from pathlib import Path


class LLVMTestPackageConan(ConanFile):
    settings = ('os', 'arch', 'compiler', 'build_type')
    generators = ('cmake', 'cmake_find_package')

    def build(self):
        build_system = CMake(self)
        build_system.configure()
        build_system.build()

    def test(self):
        test_package = not tools.cross_building(self.settings)
        if 'x86' not in str(self.settings.arch).lower():
            test_package = False
        elif str(self.options['llvm-core'].targets) not in ['all', 'X86']:
            test_package = False
        elif self.options['llvm-core'].shared:
            if self.options['llvm-core'].components != 'all':
                requirements = ['interpreter', 'irreader', 'x86codegen']
                targets = str(self.options['llvm-core'].components)
                if self.settings.os == 'Windows':
                    requirements.append('demangle')
                if not all([target in components for target in requirements]):
                    test_package = False

        if test_package:
            executable = Path('bin').joinpath('test_package')
            input = Path(__file__).parent.joinpath('test_function.ll')
            command = [str(file.resolve()) for file in (executable, input)]
            self.run(command, run_environment=True)

        llvm_path = Path(self.deps_cpp_info['llvm-core'].rootpath)
        license_file = llvm_path.joinpath('licenses', 'LICENSE.TXT')
        assert license_file.exists()
