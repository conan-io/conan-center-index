import os

from conans import ConanFile, CMake, tools


class QuickfixTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def source(self):
        self.run("""
rm -rf source || true
mkdir source
cd source
git init
git remote add origin https://github.com/quickfix/quickfix.git
git config core.sparseCheckout true
echo "examples/" >> .git/info/sparse-checkout
git pull origin master
        """)

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

    def test(self):
        if not tools.cross_building(self):
            os.chdir("bin")
            self.run(".%sexecutor" % os.sep)
