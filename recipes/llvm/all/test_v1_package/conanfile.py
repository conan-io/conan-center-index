from conans import ConanFile, CMake, tools
import os
import re


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.21.3 <4.0.0]")
        self.build_requires("ninja/[>=1.10.0 <2.0.0]")

    def _llvm_major_version(self):
        pattern = re.compile("^llvm/([0-9]+)")
        return int(re.findall(pattern, self.tested_reference_str)[0])

    def _ccpstd(self):
        cppstd = 14
        if self._llvm_major_version() >= 16:
            cppstd = 17
        return cppstd

    def build(self):
        cmake = CMake(self)
        print(self.options)
        print(self.options["llvm/14.0.6"])
        cmake.configure(defs={
            'CMAKE_CXX_STANDARD': self._ccpstd(),
            # 'llvm_build_llvm_dylib': self.options[self.tested_reference_str].llvm_build_llvm_dylib,
        })
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
