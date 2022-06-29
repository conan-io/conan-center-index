from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        compiler_env = {}
        # Workaround for https://bugs.llvm.org/show_bug.cgi?id=16404
        # Ony really for the purporses of building on CCI - end users can
        # workaround this by appropriately setting global linker flags in their profile
        if self.settings.compiler == "clang":
            compiler_env = {"LDFLAGS": "-rtlib=compiler-rt"}
        with tools.environment_append(compiler_env):
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run("gdk-pixbuf-pixdata -v", run_environment=True)
            self.run(bin_path, run_environment=True)
