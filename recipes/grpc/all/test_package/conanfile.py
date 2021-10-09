from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build_requirements(self):
        if hasattr(self, "settings_build") and tools.cross_building(self):
            self.build_requires(str(self.requires['grpc']))
            
    def build(self):
        cmake = CMake(self)

        if (
            self.settings.compiler == "gcc"
            and tools.Version(self.settings.compiler.version) >= "11"
            and not self.settings.compiler.get_safe("cppstd")
        ):
            self._cmake.definitions["CMAKE_CXX_STANDARD"] = "17"

        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join(".", "bin", "greeter_client_server")
            self.run(bin_path, run_environment=True)
