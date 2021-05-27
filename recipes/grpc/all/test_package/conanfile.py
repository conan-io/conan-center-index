from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build_requirements(self):
        if tools.cross_building(self.settings):
            # this would depend on same version from upstream
            # which may block package tests for not yet existing upstream packages
            # self.build_requires(str(self.requires["grpc"]).split("@")[0])
            # self.output.warn(self.requires) 
            # this the version number should be derived from conan package itself
            # self.build_requires("grpc/1.37.1")
            # this uses the correct conan packag version, but is not able to build locally in cross-compile toolchain like conanio/gcc9-armv7hf
            self.build_requires(str(self.requires["grpc"]))
            
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join(".", "bin", "greeter_client_server")
            self.run(bin_path, run_environment=True)
