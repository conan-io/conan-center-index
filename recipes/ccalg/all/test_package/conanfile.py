from conan import ConanFile


class CcalgTestConan(ConanFile):
    settings = ["os", "arch", "compiler", "build_type"]
    generators = ["CMakeDeps", "CMakeToolchain"]

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        from conan.tools.cmake import CMake
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        # header-only — compilation is sufficient to verify headers are accessible
        pass
