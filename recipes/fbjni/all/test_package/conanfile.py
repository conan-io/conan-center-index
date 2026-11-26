from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"

    @property
    def _system_java_home(self):
        return self.conf.get("user.fbjni:java_home") or os.environ.get("JAVA_HOME")

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        # Consumers find jni.h with find_package(JNI); use the build machine's JDK if there is one
        if not self._system_java_home:
            self.tool_requires("zulu-openjdk/21.0.11")

    def generate(self):
        tc = CMakeToolchain(self)
        java_home = self._system_java_home or self.dependencies.build["zulu-openjdk"].package_folder
        tc.cache_variables["JAVA_HOME"] = java_home.replace("\\", "/")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
