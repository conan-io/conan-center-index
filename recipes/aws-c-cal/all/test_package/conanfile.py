from conans import ConanFile, CMake, tools
import os
import io

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            stream = io.StringIO()
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True, output=stream)
            print(stream.getvalue())
            if bool(self.deps_user_info["aws-c-cal"].with_openssl):
                assert "found static libcrypto" in stream.getvalue()
