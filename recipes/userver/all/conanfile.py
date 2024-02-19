import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, export_conandata_patches, apply_conandata_patches
from conan.tools.build import cross_building
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"

class UserverConan(ConanFile):
    name = 'userver'
    description = 'The C++ Asynchronous Framework'
    topics = ('framework', 'coroutines', 'asynchronous')
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://userver.tech/'
    license = 'Apache-2.0'
    package_type = "static-library"

    settings = 'os', 'arch', 'compiler', 'build_type'
    options = {
        'fPIC': [True, False],
        'lto': [True, False],
        'with_jemalloc': [True, False],
        'with_mongodb': [True, False],
        'with_postgresql': [True, False],
        'with_postgresql_extra': [True, False],
        'with_redis': [True, False],
        'with_grpc': [True, False],
        'with_clickhouse': [True, False],
        'with_rabbitmq': [True, False],
        'with_utest': [True, False],
        'with_testsuite' : [True, False],
        'namespace': ['ANY'],
        'namespace_begin': ['ANY'],
        'namespace_end': ['ANY'],
    }

    default_options = {
        'fPIC': True,
        'lto': True,
        'with_jemalloc': False, # Disabled dy default due to jemalloc recipe does not support Conan v2
        'with_mongodb': False, # Disabled by default due to https://github.com/conan-io/conan-center-index/pull/20712#issuecomment-1781385911
        'with_postgresql': False,
        'with_postgresql_extra': False, # Disabled dy default due to https://github.com/conan-io/conan-center-index/pull/16074
        'with_redis': False,
        'with_grpc': False,
        'with_clickhouse': False,
        'with_rabbitmq': False,
        'with_utest': False,
        'with_testsuite': False,
        'namespace': 'userver',
        'namespace_begin': 'namespace userver {',
        'namespace_end': '}',
        'mongo-c-driver/*:with_sasl': 'cyrus',
    }

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "9",
            "apple-clang": "9",
        }

    @property
    def _source_subfolder(self):
        return 'source'

    @property
    def _build_subfolder(self):
        return os.path.join(self.build_folder, 'userver')

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires('boost/1.79.0', transitive_headers=True)
        self.requires('c-ares/1.19.1')
        self.requires('cctz/2.3', transitive_headers=True)
        self.requires('concurrentqueue/1.0.3', transitive_headers=True)
        self.requires('cryptopp/8.7.0')
        self.requires('fmt/8.1.1', transitive_headers=True)
        self.requires('libnghttp2/1.51.0')
        self.requires('libcurl/7.88.1')
        self.requires('libev/4.33')
        self.requires('http_parser/2.9.4')
        self.requires("openssl/[>=1.1 <4]")
        self.requires('rapidjson/cci.20220822', transitive_headers=True)
        self.requires('yaml-cpp/0.7.0')
        self.requires("zlib/[>=1.2.11 <2]")

        if self.options.with_jemalloc:
            self.requires('jemalloc/5.3.0')
        if self.options.with_grpc:
            self.requires(
                'grpc/1.54.3', transitive_headers=True, transitive_libs=True,
            )
            self.requires(
                'googleapis/cci.20230501',
                transitive_headers=True,
                transitive_libs=True,
            )
            self.requires(
                'grpc-proto/cci.20220627',
                transitive_headers=True,
                transitive_libs=True,
            )
        if self.options.with_postgresql:
            self.requires('libpq/14.5')
        if self.options.with_mongodb:
            self.requires('cyrus-sasl/2.1.27')
            self.requires(
                'mongo-c-driver/1.22.0',
                transitive_headers=True,
                transitive_libs=True,
            )
        if self.options.with_redis:
            self.requires('hiredis/1.0.2')
        if self.options.with_rabbitmq:
            self.requires('amqp-cpp/4.3.26')
        if self.options.with_clickhouse:
            self.requires('clickhouse-cpp/2.4.0')
            self.requires(
                'abseil/20230125.3',
                transitive_headers=True,
                transitive_libs=True,
            )
        if self.options.with_utest:
            self.requires(
                'gtest/1.12.1', transitive_headers=True, transitive_libs=True,
            )
            self.requires(
                'benchmark/1.6.2',
                transitive_headers=True,
                transitive_libs=True,
            )

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True,
                    destination=self.source_folder)

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("userver can't be built on Windows")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"Compiler ({self.settings.compiler} {self.settings.compiler.version}) does not supported")

        if self.options.with_mongodb:
            if self.dependencies['mongo-c-driver'].options.with_sasl != 'cyrus':
                raise ConanInvalidConfiguration(
                    f'{self.ref} requires mongo-c-driver with_sasl cyrus',
                )

        if cross_building(self):
            raise ConanInvalidConfiguration("Cross building temporarily disabled")

    def generate(self):
        apply_conandata_patches(self)
        tool_ch = CMakeToolchain(self)
        tool_ch.variables['CMAKE_FIND_DEBUG_MODE'] = False

        tool_ch.variables['USERVER_OPEN_SOURCE_BUILD'] = True
        tool_ch.variables['USERVER_CONAN'] = True
        tool_ch.variables['USERVER_IS_THE_ROOT_PROJECT'] = False
        tool_ch.variables['USERVER_DOWNLOAD_PACKAGES'] = True
        tool_ch.variables['USERVER_FEATURE_DWCAS'] = True
        tool_ch.variables['USERVER_NAMESPACE'] = self.options.namespace
        tool_ch.variables[
            'USERVER_NAMESPACE_BEGIN'
        ] = self.options.namespace_begin
        tool_ch.variables['USERVER_NAMESPACE_END'] = self.options.namespace_end

        tool_ch.variables['USERVER_LTO'] = self.options.lto
        tool_ch.variables[
            'USERVER_FEATURE_JEMALLOC'
        ] = self.options.with_jemalloc
        tool_ch.variables[
            'USERVER_FEATURE_MONGODB'
        ] = self.options.with_mongodb
        tool_ch.variables[
            'USERVER_FEATURE_POSTGRESQL'
        ] = self.options.with_postgresql
        tool_ch.variables[
            'USERVER_FEATURE_PATCH_LIBPQ'
        ] = self.options.with_postgresql_extra
        tool_ch.variables['USERVER_FEATURE_REDIS'] = self.options.with_redis
        tool_ch.variables['USERVER_FEATURE_GRPC'] = self.options.with_grpc
        tool_ch.variables[
            'USERVER_FEATURE_CLICKHOUSE'
        ] = self.options.with_clickhouse
        tool_ch.variables[
            'USERVER_FEATURE_RABBITMQ'
        ] = self.options.with_rabbitmq
        tool_ch.variables['USERVER_FEATURE_UTEST'] = self.options.with_utest
        tool_ch.variables['USERVER_FEATURE_TESTSUITE'] = self.options.with_testsuite

        # Temporarily disable DWCAS when cross
        # if cross_building(self):
        #    tool_ch.variables['USERVER_FEATURE_DWCAS'] = False
        
        tool_ch.generate()

        CMakeDeps(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _userver_root(self):
        return os.path.join(self.package_folder, 'lib')

    @property
    def _cmake_subfolder(self):
        return os.path.join(self.package_folder, 'lib', 'cmake')

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder,"licenses")
        )

        copy(
            self,
            pattern='*',
            dst=os.path.join(self._userver_root, 'scripts'),
            src=os.path.join(self.source_folder, 'scripts'),
            keep_path=True,
        )

        copy(
            self,
            pattern='*',
            dst=os.path.join(
                self.package_folder, 'include', 'function_backports',
            ),
            src=os.path.join(
                self.source_folder,
                'third_party',
                'function_backports',
                'include',
            ),
            keep_path=True,
        )

        def copy_component(component):
            copy(
                self,
                pattern='*',
                dst=os.path.join(self.package_folder, 'include', component),
                src=os.path.join(self.source_folder, component, 'include'),
                keep_path=True,
            )
            copy(
                self,
                pattern='*.a',
                dst=os.path.join(self.package_folder, 'lib'),
                src=os.path.join(self._build_subfolder, component),
                keep_path=False,
            )
            copy(
                self,
                pattern='*.so',
                dst=os.path.join(self.package_folder, 'lib'),
                src=os.path.join(self._build_subfolder, component),
                keep_path=False,
            )

        copy_component('core')
        copy_component('universal')

        os.makedirs(self._cmake_subfolder)
        with open(
                os.path.join(
                    self._cmake_subfolder, 'conan_helper.cmake',
                ),
                    'a+',
        ) as cmake_file:
            cmake_file.write('\nset(USERVER_CONAN TRUE)')
            cmake_file.write('\nset(PYTHON "python3")')
            cmake_file.write(f'\nset(USERVER_ROOT_DIR {self._userver_root})')

        if self.options.with_grpc:
            copy_component('grpc')
            copy(
                self,
                pattern='*',
                dst=os.path.join(self.package_folder, 'include', 'grpc'),
                src=os.path.join(
                    self.source_folder, 'grpc', 'handlers', 'include',
                ),
                keep_path=True,
            )
            copy(
                self,
                pattern='GrpcTargets.cmake',
                dst=self._cmake_subfolder,
                src=os.path.join(self.source_folder, 'cmake'),
                keep_path=True,
            )

        if self.options.with_utest:
            copy(
                self,
                pattern='*',
                dst=os.path.join(self.package_folder, 'include', 'utest'),
                src=os.path.join(
                    self.source_folder, 'core', 'testing', 'include',
                ),
                keep_path=True,
            )
            copy(
                self,
                pattern='*',
                dst=os.path.join(self._userver_root, 'testsuite'),
                src=os.path.join(self.source_folder, 'testsuite'),
                keep_path=True,
            )
            copy(
                self,
                pattern='AddGoogleTests.cmake',
                dst=self._cmake_subfolder,
                src=os.path.join(self.source_folder, 'cmake'),
                keep_path=True,
            )
        if self.options.with_grpc or self.options.with_utest:
            copy(
                self,
                pattern='UserverTestsuite.cmake',
                dst=self._cmake_subfolder,
                src=os.path.join(self.source_folder, 'cmake'),
                keep_path=True,
            )
        if self.options.with_postgresql:
            copy_component('postgresql')

        if self.options.with_mongodb:
            copy_component('mongo')

        if self.options.with_redis:
            copy_component('redis')

        if self.options.with_rabbitmq:
            copy_component('rabbitmq')

        if self.options.with_clickhouse:
            copy_component('clickhouse')

    @property
    def _userver_components(self):
        def ares():
            return ['c-ares::c-ares']

        def fmt():
            return ['fmt::fmt']

        def curl():
            return ['libcurl::libcurl']

        def cryptopp():
            return ['cryptopp::cryptopp']

        def cctz():
            return ['cctz::cctz']

        def boost():
            return ['boost::boost']

        def concurrentqueue():
            return ['concurrentqueue::concurrentqueue']

        def yaml():
            return ['yaml-cpp::yaml-cpp']

        def libev():
            return ['libev::libev']

        def http_parser():
            return ['http_parser::http_parser']

        def libnghttp2():
            return ['libnghttp2::libnghttp2']

        def openssl():
            return ['openssl::openssl']

        def rapidjson():
            return ['rapidjson::rapidjson']

        def zlib():
            return ['zlib::zlib']

        def jemalloc():
            return ['jemalloc::jemalloc'] if self.options.with_jemalloc else []

        def grpc():
            return ['grpc::grpc'] if self.options.with_grpc else []

        def googleapis():
            return ['googleapis::googleapis'] if self.options.with_grpc else []

        def grpcproto():
            return ['grpc-proto::grpc-proto'] if self.options.with_grpc else []

        def postgresql():
            return ['libpq::pq'] if self.options.with_postgresql else []

        def gtest():
            return ['gtest::gtest'] if self.options.with_utest else []

        def benchmark():
            return ['benchmark::benchmark'] if self.options.with_utest else []

        def mongo():
            return (
                ['mongo-c-driver::mongo-c-driver']
                if self.options.with_mongodb
                else []
            )

        def cyrussasl():
            return (
                ['cyrus-sasl::cyrus-sasl'] if self.options.with_mongodb else []
            )

        def hiredis():
            return ['hiredis::hiredis'] if self.options.with_redis else []

        def amqpcpp():
            return ['amqp-cpp::amqp-cpp'] if self.options.with_rabbitmq else []

        def clickhouse():
            return (
                ['clickhouse-cpp::clickhouse-cpp']
                if self.options.with_clickhouse
                else []
            )

        def abseil():
            return (
                ['abseil::abseil']
                if self.options.with_clickhouse
                else []
            )


        userver_components = [
            {
                'target': 'core',
                'lib': 'core',
                'requires': (
                    abseil()
                    + fmt()
                    + cctz()
                    + boost()
                    + concurrentqueue()
                    + yaml()
                    + libev()
                    + http_parser()
                    + libnghttp2()
                    + curl()
                    + cryptopp()
                    + jemalloc()
                    + ares()
                    + rapidjson()
                    + zlib()
                ),
            },
            {
                    'target': 'universal',
                    'lib': 'universal',
                    'requires': (
                        fmt()
                        + cctz()
                        + boost()
                        + concurrentqueue()
                        + yaml()
                        + cryptopp()
                        + jemalloc()
                        + openssl()
                    ),
            },
        ]

        if self.options.with_grpc:
            userver_components.extend(
                [
                    {
                        'target': 'grpc',
                        'lib': 'grpc',
                        'requires': (
                            ['core']
                            + grpc()
                            + googleapis()
                            + grpcproto()
                        ),
                    },
                    {
                        'target': 'grpc-handlers',
                        'lib': 'grpc-handlers',
                        'requires': ['core'] + grpc(),
                    },
                    {
                        'target': 'grpc-handlers-proto',
                        'lib': 'grpc-handlers-proto',
                        'requires': ['core'] + grpc(),
                    },
                    {
                        'target': 'api-common-protos',
                        'lib': 'api-common-protos',
                        'requires': ['grpc'],
                    },
                ],
            )
        if self.options.with_utest:
            userver_components.extend(
                [
                    {
                        'target': 'utest',
                        'lib': 'utest',
                        'requires': ['core'] + gtest(),
                    },
                    {
                        'target': 'ubench',
                        'lib': 'ubench',
                        'requires': ['core'] + benchmark(),
                    },
                ],
            )
        if self.options.with_postgresql:
            userver_components.extend(
                [
                    {
                        'target': 'postgresql',
                        'lib': 'postgresql',
                        'requires': ['core'] + postgresql(),
                    },
                ],
            )
        if self.options.with_mongodb:
            userver_components.extend(
                [
                    {
                        'target': 'mongo',
                        'lib': 'mongo',
                        'requires': ['core'] + mongo() + cyrussasl(),
                    },
                ],
            )
        if self.options.with_redis:
            userver_components.extend(
                [
                    {
                        'target': 'redis',
                        'lib': 'redis',
                        'requires': ['core'] + hiredis(),
                    },
                ],
            )
        if self.options.with_rabbitmq:
            userver_components.extend(
                [
                    {
                        'target': 'rabbitmq',
                        'lib': 'rabbitmq',
                        'requires': ['core'] + amqpcpp(),
                    },
                ],
            )
        if self.options.with_clickhouse:
            userver_components.extend(
                [
                    {
                        'target': 'clickhouse',
                        'lib': 'clickhouse',
                        'requires': ['core'] + clickhouse(),
                    },
                ],
            )
        return userver_components

    def package_info(self):

        debug = (
            'd'
            if self.settings.build_type == 'Debug'
            and self.settings.os == 'Windows'
            else ''
        )

        def get_lib_name(module):
            return f'userver-{module}{debug}'

        def add_components(components):
            for component in components:
                conan_component = component['target']
                cmake_target = component['target']
                cmake_component = component['lib']
                lib_name = get_lib_name(component['lib'])
                requires = component['requires']
                # TODO: we should also define COMPONENTS names of each target
                # for find_package() but not possible yet in CMakeDeps
                #       see https://github.com/conan-io/conan/issues/10258
                self.cpp_info.components[conan_component].set_property(
                    'cmake_target_name', 'userver::' + cmake_target,
                )
                if cmake_component == 'grpc':
                    self.cpp_info.components[conan_component].libs.append(
                        get_lib_name('grpc-internal'),
                    )
                if cmake_component == 'core':
                    self.cpp_info.components[conan_component].libs.append(
                        get_lib_name('core-internal'),
                    )
                self.cpp_info.components[conan_component].libs = [lib_name]
                if cmake_component == 'universal':
                    self.cpp_info.components[
                        cmake_component
                    ].includedirs.append(
                        os.path.join('include', 'function_backports'),
                    )
                if cmake_component not in ['ubench', 'grpc-handlers', 'grpc-handlers-proto', 'api-common-protos']:
                    self.cpp_info.components[
                        conan_component
                    ].includedirs.append(
                        os.path.join('include', cmake_component),
                    )

                self.cpp_info.components[conan_component].requires = requires

        self.cpp_info.components['core'].defines.append(
            f'USERVER_NAMESPACE={self.options.namespace}',
        )
        self.cpp_info.components['core'].defines.append(
            f'USERVER_NAMESPACE_BEGIN={self.options.namespace_begin}',
        )
        self.cpp_info.components['core'].defines.append(
            f'USERVER_NAMESPACE_END={self.options.namespace_end}',
        )

        self.cpp_info.components['universal'].defines.append(
            f'USERVER_NAMESPACE={self.options.namespace}',
        )
        self.cpp_info.components['universal'].defines.append(
            f'USERVER_NAMESPACE_BEGIN={self.options.namespace_begin}',
        )
        self.cpp_info.components['universal'].defines.append(
            f'USERVER_NAMESPACE_END={self.options.namespace_end}',
        )

        self.cpp_info.set_property('cmake_file_name', 'userver')

        add_components(self._userver_components)

        build_modules = [
            os.path.join(self._cmake_subfolder, 'conan_helper.cmake'),
        ]

        if self.options.with_testsuite:
            build_modules.append(
                os.path.join(self._cmake_subfolder, 'UserverTestsuite.cmake'),
            )

        if self.options.with_utest:
            build_modules.append(
                os.path.join(self._cmake_subfolder, 'AddGoogleTests.cmake'),
            )
        if self.options.with_grpc:
            build_modules.append(
                os.path.join(self._cmake_subfolder, 'GrpcTargets.cmake'),
            )

        self.cpp_info.set_property('cmake_build_modules', build_modules)
