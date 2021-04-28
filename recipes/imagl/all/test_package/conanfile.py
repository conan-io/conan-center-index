import os
from conans import ConanFile, CMake, tools


class ImaglTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        # CMake generator must be set to Ninja when using Visual Studio to let choose the right 
        # MSVC compiler version when multiple versions are installed on build machine. The problem
        # with default generator is that it will always choose the last MSVC version. It will 
        # generate Visual Studio solution and project files, and use MSBuild to build it. I think 
        # it's a "feature" of CMake / Visual Studio generator that does not use environment which 
        # is set by vcvars. So if you want to use a specific MSVC version, you have to use Ninja 
        # generator with CMake. You can find some side explanation here: 
        # https://devblogs.microsoft.com/cppblog/side-by-side-minor-version-msvc-toolsets-in-visual-studio-2019/
        # 
        # Building with specific MSVC version could be needed since imaGL requires some minimal 
        # version to be compiled according to its own version. Following table links imaGL version 
        # to minimal MSVC version:
        # 
        # | imaGL version |    MSVC minimal version    |
        # |---------------|----------------------------|
        # |         0.1.0 | 19.25 (default in VS 16.5) |
        # |         0.1.1 | 19.25 (default in VS 16.5) |
        # |         0.1.2 | 19.22 (default in VS 16.2) |
        # |         0.2.0 | 19.25 (default in VS 16.5) |
        # |         0.2.1 | 19.22 (default in VS 16.2) |
        #
        generator = "Ninja" if str(self.settings.compiler) == "Visual Studio" else None
        cmake = CMake(self, generator=generator)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "example")
            self.run(bin_path, run_environment=True)
