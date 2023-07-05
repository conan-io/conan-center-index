# pylint: skip-file
from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        # when --static-linked-ext is used, ruby defines EXTSTATIC as 1
        # But when ruby itself is static there's nothing, so:
        # We define RUBY_STATIC_RUBY when ruby itself is static
        # We define RUBY_STATIC_LINKED_EXT when the ruby extensions are static (same as EXTSTATIC but clearer)
        if not self.options['ruby'].shared:
            cmake.definitions['RUBY_STATIC_RUBY'] = 1
            if self.options['ruby'].with_static_linked_ext:
                cmake.definitions['RUBY_STATIC_LINKED_EXT'] = 1
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            # test executable
            self.run("ruby --version", run_environment=True)

            # test library
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
