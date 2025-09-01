# pylint: disable=no-member
import os
import platform
import re

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake
from conan.tools.cmake import cmake_layout
from conan.tools.cmake import CMakeDeps
from conan.tools.cmake import CMakeToolchain
from conan.tools.files import get, copy, export_conandata_patches
from conan.tools.files import load
from conan.tools.scm import Git
from conan.tools.system import package_manager

required_conan_version = '>=2.8.0'  # pylint: disable=invalid-name


class UserverConan(ConanFile):
    name = 'userver'
    description = 'The C++ Asynchronous Framework'
    topics = ('framework', 'coroutines', 'asynchronous')
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://userver.tech/'
    license = 'Apache-2.0'
    package_type = 'static-library'

    settings = 'os', 'arch', 'compiler', 'build_type'
    options = {
        'fPIC': [True, False],
        'lto': [True, False],
        'with_jemalloc': [True, False],
        'with_mongodb': [True, False],
        'with_postgresql': [True, False],
        'with_postgresql_extra': [True, False],
        'with_redis': [True, False],
        'with_redis_tls': [True, False],
        'with_grpc': [True, False],
        'with_clickhouse': [True, False],
        'with_rabbitmq': [True, False],
        'with_utest': [True, False],
        'with_kafka': [True, False],
        'with_otlp': [True, False],
        'with_sqlite': [True, False],
        'with_easy': [True, False],
        'with_s3api': [True, False],
        'with_grpc_reflection': [True, False],
        'with_grpc_protovalidate': [True, False],
        'namespace': ['ANY'],
        'namespace_begin': ['ANY'],
        'namespace_end': ['ANY'],
        'python_path': ['ANY'],
    }

    default_options = {
        'fPIC': True,
        'lto': False,
        'with_jemalloc': (platform.system() != 'Darwin'),
        'with_mongodb': True,
        'with_postgresql': True,
        'with_postgresql_extra': False,
        'with_redis': True,
        'with_redis_tls': True,
        'with_grpc': True,
        'with_clickhouse': True,
        'with_rabbitmq': True,
        'with_utest': True,
        'with_kafka': True,
        'with_otlp': True,
        'with_sqlite': True,
        'with_easy': True,
        'with_s3api': True,
        'with_grpc_reflection': True,
        'with_grpc_protovalidate': False,
        'namespace': 'userver',
        'namespace_begin': 'namespace userver {',
        'namespace_end': '}',
        'python_path': 'python3',
        'mongo-c-driver/*:with_sasl': 'cyrus',
        'grpc/*:php_plugin': False,
        'grpc/*:node_plugin': False,
        'grpc/*:ruby_plugin': False,
        'grpc/*:csharp_plugin': False,
        'grpc/*:objective_c_plugin': False,
        'hiredis/*:with_ssl': True,
        'librdkafka/*:ssl': True,
        'librdkafka/*:curl': True,
        'librdkafka/*:sasl': True,
        'librdkafka/*:zlib': True,
        'librdkafka/*:zstd': True,
        're2/*:with_icu': True,
    }

    def source(self):
        known_version = (self.conan_data or {}).get("sources", {}).get(self.version)
        if known_version:
            get(self, **known_version, strip_root=True)
        else:
            Git(self).clone('https://github.com/userver-framework/userver.git', target='.')

    def export_sources(self):
        known_version = (self.conan_data or {}).get("sources", {}).get(self.version)
        if known_version:
            export_conandata_patches(self)
        else:
            pass  # Running from develop branch, no patches

    def set_version(self):
        if self.version:
            return

        content = load(
            self,
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'cmake/GetUserverVersion.cmake',
            ),
        )
        major_version = re.search(r'set\(USERVER_MAJOR_VERSION (.*)\)', content).group(1).strip()
        minor_version = re.search(r'set\(USERVER_MINOR_VERSION (.*)\)', content).group(1).strip()

        self.version = f'{major_version}.{minor_version}'  # pylint: disable=attribute-defined-outside-init

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires('boost/1.86.0', transitive_headers=True)
        self.requires('c-ares/1.33.1')
        self.requires('cctz/2.4', transitive_headers=True)
        self.requires('concurrentqueue/1.0.3', transitive_headers=True)
        self.requires('cryptopp/8.9.0')
        self.requires('fmt/11.0.2', transitive_headers=True)
        self.requires('libiconv/1.17')
        self.requires('libnghttp2/1.61.0')
        self.requires('libcurl/7.86.0')
        self.requires('libev/4.33')
        self.requires('openssl/3.3.2')
        self.requires('rapidjson/cci.20220822', transitive_headers=True)
        self.requires('yaml-cpp/0.8.0')
        self.requires('zlib/1.3.1')
        self.requires('zstd/1.5.5')
        self.requires('icu/74.1', force=True)
        self.requires('re2/20230301')

        if self.options.with_jemalloc:
            self.requires('jemalloc/5.3.0')
        if self.options.with_grpc or self.options.with_clickhouse:
            self.requires('abseil/20240116.2', force=True)
        if self.options.with_grpc:
            self.requires(
                'grpc/1.65.0',
                transitive_headers=True,
                transitive_libs=True,
            )
            self.requires(
                'protobuf/5.27.0',
                transitive_headers=True,
                transitive_libs=True,
                force=True,
            )
            self.requires('googleapis/cci.20230501')
        if self.options.with_postgresql:
            # `run=True` required to find `pg_config` binary during `psycopg2` python module build
            # without system package. We use system package.
            self.requires('libpq/14.9')
        if self.options.with_mongodb or self.options.with_kafka:
            self.requires('cyrus-sasl/2.1.28')
        if self.options.with_mongodb:
            self.requires(
                'mongo-c-driver/1.28.0',
                transitive_headers=True,
                transitive_libs=True,
            )
        if self.options.with_redis:
            self.requires('hiredis/1.2.0')
        if self.options.with_rabbitmq:
            self.requires('amqp-cpp/4.3.26')
        if self.options.with_clickhouse:
            self.requires('clickhouse-cpp/2.5.1')
        if self.options.with_utest:
            self.requires(
                'gtest/1.15.0',
                transitive_headers=True,
                transitive_libs=True,
            )
            self.requires(
                'benchmark/1.9.0',
                transitive_headers=True,
                transitive_libs=True,
            )
        if self.options.with_kafka:
            self.requires('librdkafka/2.6.0')
        if self.options.with_sqlite:
            self.requires('sqlite3/3.46.1')
        if self.options.with_s3api:
            self.requires('pugixml/1.14')
        if self.options.with_otlp:
            self.requires('opentelemetry-proto/1.3.0')

    def build_requirements(self):
        self.tool_requires('protobuf/5.27.0')

    def validate(self):
        if self.settings.os == 'Windows':
            raise ConanInvalidConfiguration(
                'userver cannot be built on Windows',
            )

        if self.options.with_mongodb and self.dependencies['mongo-c-driver'].options.with_sasl != 'cyrus':
            raise ConanInvalidConfiguration(
                f'{self.ref} requires mongo-c-driver with_sasl cyrus',
            )

    def generate(self):
        tool_ch = CMakeToolchain(self)
        tool_ch.variables['CMAKE_FIND_DEBUG_MODE'] = False

        tool_ch.variables['USERVER_CONAN'] = True
        tool_ch.variables['USERVER_INSTALL'] = True
        tool_ch.variables['USERVER_DOWNLOAD_PACKAGES'] = True
        tool_ch.variables['USERVER_FEATURE_DWCAS'] = True
        tool_ch.variables['USERVER_NAMESPACE'] = self.options.namespace
        tool_ch.variables['USERVER_NAMESPACE_BEGIN'] = self.options.namespace_begin
        tool_ch.variables['USERVER_NAMESPACE_END'] = self.options.namespace_end
        tool_ch.variables['USERVER_PYTHON_PATH'] = self.options.python_path

        tool_ch.variables['USERVER_LTO'] = self.options.lto
        tool_ch.variables['USERVER_FEATURE_JEMALLOC'] = self.options.with_jemalloc
        tool_ch.variables['USERVER_FEATURE_MONGODB'] = self.options.with_mongodb
        tool_ch.variables['USERVER_FEATURE_POSTGRESQL'] = self.options.with_postgresql
        tool_ch.variables['USERVER_FEATURE_PATCH_LIBPQ'] = self.options.with_postgresql_extra
        tool_ch.variables['USERVER_FEATURE_REDIS'] = self.options.with_redis
        tool_ch.variables['USERVER_FEATURE_REDIS_TLS'] = self.options.with_redis_tls
        tool_ch.variables['USERVER_FEATURE_GRPC'] = self.options.with_grpc
        tool_ch.variables['USERVER_FEATURE_CLICKHOUSE'] = self.options.with_clickhouse
        tool_ch.variables['USERVER_FEATURE_RABBITMQ'] = self.options.with_rabbitmq
        tool_ch.variables['USERVER_FEATURE_UTEST'] = self.options.with_utest
        tool_ch.variables['USERVER_FEATURE_TESTSUITE'] = self.options.with_utest
        tool_ch.variables['USERVER_FEATURE_KAFKA'] = self.options.with_kafka
        tool_ch.variables['USERVER_FEATURE_OTLP'] = self.options.with_otlp
        tool_ch.variables['USERVER_FEATURE_SQLITE'] = self.options.with_sqlite
        tool_ch.variables['USERVER_FEATURE_EASY'] = self.options.with_easy
        tool_ch.variables['USERVER_FEATURE_S3API'] = self.options.with_s3api
        tool_ch.variables['USERVER_FEATURE_GRPC_REFLECTION'] = self.options.with_grpc_reflection
        tool_ch.variables['USERVER_FEATURE_GRPC_PROTOVALIDATE'] = self.options.with_grpc_protovalidate

        if self.options.with_grpc:
            tool_ch.variables['USERVER_GOOGLE_COMMON_PROTOS'] = (
                self.dependencies['googleapis'].cpp_info.components['google_rpc_status_proto'].resdirs[0]
            )

        if self.options.with_otlp:
            tool_ch.variables['USERVER_OPENTELEMETRY_PROTO'] = self.dependencies['opentelemetry-proto'].conf_info.get(
                'user.opentelemetry-proto:proto_root'
            )

        tool_ch.generate()

        CMakeDeps(self).generate()

    def build(self):
        # pg_config is required to build psycopg2 from source without system package.
        # However, this approach fails on later stage, when venv for tests is built.
        # libpq = self.dependencies["libpq"]
        # if libpq:
        #     os.environ["PATH"] = os.environ["PATH"] + ":" + libpq.package_folder+ "/bin"

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # https://docs.conan.io/2/examples/tools/cmake/cmake_toolchain/use_package_config_cmake.html
        self.cpp_info.set_property('cmake_find_mode', 'none')
        self.cpp_info.builddirs.append(os.path.join('lib', 'cmake', 'userver'))

    def system_requirements(self):
        if self.options.with_postgresql:
            # pg_config is required to build psycopg2 python module from source at
            # testsuite venv creation during functional testing of user code.
            package_manager.Apt(self).install(['libpq-dev'])
            package_manager.Yum(self).install(['libpq-devel'])
            package_manager.PacMan(self).install(['libpq-dev'])
            package_manager.Zypper(self).install(['libpq-devel'])
