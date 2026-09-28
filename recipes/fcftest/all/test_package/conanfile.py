from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, f"https://github.com/fcf-framework/fcfTest/archive/refs/tags/v{self.version}.zip", strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not self.options.get_safe("cross_building"):
            # 1. Запуск стандартной заглушки Conan
            cmd_package = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(cmd_package, env="conanrun")

            # 2. ЗАПУСК ВАШИХ ВСТРОЕННЫХ ТЕСТОВ
            # Замените "fcftest-tests" на реальное имя исполняемого файла из вашего CMakeLists.txt
            cmd_internal = os.path.join(self.cpp.build.bindir, "fcf-test-test")
            if self.settings.os == "Windows":
                cmd_internal += ".exe"

            self.output.info(f"Running embedded library tests: {cmd_internal}")
            self.run(cmd_internal, env="conanrun")

