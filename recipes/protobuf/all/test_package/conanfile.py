import os
from conans import ConanFile, CMake, RunEnvironment, tools
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    @property
    def _protoc_available(self):
        return not self.options["protobuf"].lite and not tools.cross_building(self.settings)

    def build(self):
        # Build without protoc
        os.mkdir("without_protoc")
        shutil.copy(os.path.join(self.source_folder, "addressbook.{}.pb.h".format(self.deps_cpp_info["protobuf"].version)),
                    os.path.join("without_protoc", "addressbook.pb.h"))
        shutil.copy(os.path.join(self.source_folder, "addressbook.{}.pb.cc".format(self.deps_cpp_info["protobuf"].version)),
                    os.path.join("without_protoc", "addressbook.pb.cc"))
        cmake = CMake(self)
        cmake.definitions["protobuf_VERBOSE"] = True
        cmake.definitions["protobuf_MODULE_COMPATIBLE"] = True
        cmake.definitions["PROTOC_AVAILABLE"] = False
        cmake.configure(build_folder="without_protoc")
        cmake.build()

        with tools.environment_append(RunEnvironment(self).vars):
            if self._protoc_available:
                # Build with protoc
                cmake = CMake(self)
                cmake.definitions["protobuf_VERBOSE"] = True
                cmake.definitions["protobuf_MODULE_COMPATIBLE"] = True
                cmake.definitions["PROTOC_AVAILABLE"] = True
                cmake.configure(build_folder="with_protoc")
                cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("protoc --version", run_environment=True)

            # Test the build built without protoc
            bin_path = os.path.join("without_protoc", "bin", "test_package")
            self.run(bin_path, run_environment=True)

            if self._protoc_available:
                # Test the build built with protoc
                assert os.path.isfile(os.path.join("with_protoc", "addressbook.pb.cc"))
                assert os.path.isfile(os.path.join("with_protoc", "addressbook.pb.h"))
                bin_path = os.path.join("with_protoc", "bin", "test_package")
                self.run(bin_path, run_environment=True)
