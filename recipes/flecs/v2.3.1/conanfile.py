from conans import ConanFile, CMake, tools


class FlecsConan(ConanFile):
    _author = 'SanderMertens'
    _source_subfolder = 'source_subfolder'
    _build_subfolder = 'build_subfolder'

    name = 'flecs'
    version = 'v2.3.1'
    license = 'MIT'

    description = 'A fast entity component system (ECS) for C & C++'
    topics = ('lightweight', 'gamedev', 'game-engine', 'cpp', 'data-oriented-design', 'c99', 'game-development', 'ecs', 'entity-component-system', 'cpp11', 'simulation-framework', 'game-programming',
              'architectural-patterns', 'indiedev', 'gamedev-framework', 'data-oriented', 'indiegame', 'game-dev', 'simulation-engine', 'ecs-framework')

    url = f'https://github.com/conan-io/conan-center-index'
    homepage = f'https://github.com/{_author}/{name}'

    no_copy_source = True
    exports_sources = ['CMakeLists.txt']
    generators = 'cmake'

    settings = 'os', 'arch', 'compiler', 'build_type'

    options = {'shared': [True, False]}
    default_options = {'shared': False}

    def config_options(self):
        pass

    def requirements(self):
        pass

    def source(self):
        git = tools.Git(folder=self._source_subfolder)
        git.clone(f'https://github.com/{self._author}/{self.name}', self.version)

    def build(self):
        target = self.name if self.options.shared else f'{self.name}_static'

        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build(target=target)

    def package(self):
        self.copy(pattern='LICENSE', dst='licenses', src=self._source_subfolder)

        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
