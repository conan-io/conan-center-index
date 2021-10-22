import os

from conans import ConanFile, CMake, tools


class XsimdTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)

        cxxflags = cmake.definitions.get("CONAN_CXX_FLAGS", "")
        arch = str(self.settings.arch)
        if arch.startswith("x86"):
            cxxflags += " -DXSIMD_FORCE_X86_INSTR_SET=50000000"
        elif arch.startswith("ppc"):
            cxxflags += " -DXSIMD_FORCE_PPC_INSTR_SET=20000000"
        elif arch.startswith("arm"):
            cxxflags += " -DXSIMD_FORCE_ARM_INSTR_SET=81000000"
        cmake.definitions["CONAN_CXX_FLAGS"] = cxxflags

        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
