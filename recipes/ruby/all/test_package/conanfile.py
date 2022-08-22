from conan import ConanFile
from conan.tools.cmake import CMake
from conans import tools
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def build(self):

        cmake = CMake(self)
        # when --static-linked-ext is used, ruby defines EXTSTATIC as 1
        # But when ruby itself is static there's nothing, so:
        # We define RUBY_STATIC_RUBY when ruby itself is static
        # We define RUBY_STATIC_LINKED_EXT when the ruby extensions are static (same as EXTSTATIC but clearer)
        defs = {}
        if not self.options['ruby'].shared:
            defs['RUBY_STATIC_RUBY'] = 1
            if self.options['ruby'].with_static_linked_ext:
                defs['RUBY_STATIC_LINKED_EXT'] = 1
        cmake.configure(variables=defs)
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            # test executable
            self.run("ruby --version", run_environment=True)

            # test library
            self.run(os.path.join("bin", "test_package"), run_environment=True)
