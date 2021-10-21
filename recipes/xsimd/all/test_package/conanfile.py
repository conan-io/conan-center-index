import os

from conans import ConanFile, CMake, tools


class XsimdTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        arch = str(self.settings.arch)
        if arch.startswith("x86"):
            cmake.definitions["CONAN_C_FLAGS"] += " -DXSIMD_FORCE_X86_INSTR_SET"
        elif arch.startswith("ppc"):
            cmake.definitions["CONAN_C_FLAGS"] += " -DXSIMD_FORCE_PPC_INSTR_SET"
        elif arch.startswith("arm"):
            cmake.definitions["CONAN_C_FLAGS"] += " -DXSIMD_FORCE_ARM_INSTR_SET"

        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
