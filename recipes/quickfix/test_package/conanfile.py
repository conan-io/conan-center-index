import os
import shutil

from conans import ConanFile, CMake, tools


class QuickfixTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def source(self):
        shutil.rmtree("source", ignore_errors=True)
        os.makedirs("source")
        os.chdir("source")
        self.run("git init")
        self.run("git remote add origin https://github.com/quickfix/quickfix.git")
        self.run("git config core.sparseCheckout true")
        self.run("echo examples/ >> .git/info/sparse-checkout")
        self.run("git pull origin master")

    def build(self):
        cmake = CMake(self)
        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is
        # in "test_package"
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy('*.so*', dst='bin', src='lib')
        self.copy('*.lib*', dst='lib', src='lib')
        self.copy('*.a*', dst='lib', src='lib')

    def test(self):
        if not tools.cross_building(self):
            os.chdir("bin")

            if self.settings.os == "Windows":
                program = "executor_cpp"
            else:
                program = "executor"

            self.run(f".{os.sep}{program}")
