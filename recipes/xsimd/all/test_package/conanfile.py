import os

from conans import ConanFile, CMake, tools


class XsimdTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)

        cflags = cmake.definitions.get("CONAN_C_FLAGS", "")

        arch = str(self.settings.arch)
        if arch.startswith("x86"):
            cflags += " -DXSIMD_FORCE_X86_INSTR_SET"
        elif arch.startswith("ppc"):
            cflags += " -DXSIMD_FORCE_PPC_INSTR_SET"
        elif arch.startswith("arm"):
            cflags += " -DXSIMD_FORCE_ARM_INSTR_SET"

        cmake.definitions["CONAN_C_FLAGS"] = cflags

        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
