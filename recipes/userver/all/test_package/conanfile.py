import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake
from conan.tools.cmake import cmake_layout


class TestPackageConan(ConanFile):
    settings = 'os', 'arch', 'compiler', 'build_type'
    generators = 'CMakeToolchain', 'CMakeDeps', 'VirtualRunEnv'
    test_type = 'explicit'

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(
                self.cpp.build.bindirs[0], 'PackageTest_core',
            )
            self.run(bin_path, env='conanrun')

            if self.dependencies[self.tested_reference_str].options.with_utest:
                bin_path = os.path.join(
                    self.cpp.build.bindirs[0], 'PackageTest_utest',
                )
            if self.dependencies[self.tested_reference_str].options.with_grpc:
                self.run(bin_path, env='conanrun')
                bin_path = os.path.join(
                    self.cpp.build.bindirs[0], 'PackageTest_grpc',
                )
            if self.dependencies[self.tested_reference_str].options.with_mongodb:
                self.run(bin_path, env='conanrun')
                bin_path = os.path.join(
                    self.cpp.build.bindirs[0], 'PackageTest_mongo',
                )
            if self.dependencies[self.tested_reference_str].options.with_postgresql:
                self.run(bin_path, env='conanrun')
                bin_path = os.path.join(
                    self.cpp.build.bindirs[0], 'PackageTest_postgresql',
                )
            if self.dependencies[self.tested_reference_str].options.with_rabbitmq:
                self.run(bin_path, env='conanrun')
                bin_path = os.path.join(
                    self.cpp.build.bindirs[0], 'PackageTest_rabbitmq',
                )
            if self.dependencies[self.tested_reference_str].options.with_redis:
                self.run(bin_path, env='conanrun')
                bin_path = os.path.join(
                    self.cpp.build.bindirs[0], 'PackageTest_redis',
                )
            if self.dependencies[self.tested_reference_str].options.with_clickhouse:
                self.run(bin_path, env='conanrun')
                bin_path = os.path.join(
                    self.cpp.build.bindirs[0], 'PackageTest_clickhouse',
                )
            self.run(bin_path, env='conanrun')
            bin_path = os.path.join(
                self.cpp.build.bindirs[0], 'PackageTest_universal',
            )
            self.run(bin_path, env='conanrun')

            if self.dependencies[self.tested_reference_str].options.with_testsuite:
                bin_path = os.path.join(
                    self.cpp.build.bindirs[0],
                    'hello_service',
                    'runtests-testsuite-conan-samples-hello_service',
                )
                command = ' '
                folder = os.path.join(
                    self.source_folder,
                    'hello_service',
                )
                args = [bin_path, '--service-logs-pretty', '-vv', folder]
                self.run(command.join(args), env='conanrun')
