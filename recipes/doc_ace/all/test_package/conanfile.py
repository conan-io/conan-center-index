from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os
from conan.errors import ConanInvalidConfiguration
from conan.internal.model.cpp_info import CppInfo


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        
        tao_info: CppInfo = self.dependencies.get(self.tested_reference_str).cpp_info
        if tao_info is None:
            raise ConanInvalidConfiguration("TAO not found in dependencies")
        
        cflags_str = " ".join([f"-I{d}" for d in tao_info.includedirs])
        self.output.info(f"CCFLAGS: {cflags_str}")
        
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
