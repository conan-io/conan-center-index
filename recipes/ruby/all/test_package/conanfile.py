from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

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
        if not cross_building(self):
            # test executable
            self.run("ruby --version", env="conanrun")

            # test library
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
