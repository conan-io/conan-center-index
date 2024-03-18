import os

from conans import ConanFile, CMake, tools
from conan.tools.build import can_run


# Due to SIP limitations on newer macOS, `DYLD_LIBRARY_PATH`, which is set by
# `tools.run_environment`, will not be propagated properly, see
# https://stackoverflow.com/questions/35568122/why-isnt-dyld-library-path-being-propagated-here
# and https://github.com/conan-io/conan/issues/10668
def macos_shared(cf: ConanFile):
    return (tools.cross_building(cf) or cf.settings.os == "Macos") and cf.options["google-cloud-cpp"].shared

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        if macos_shared(self):
            self.output.warning("Skipping build of test_v1_package due to limitation propagating "
                                "runtime environment when invoking protoc and grpc_cpp_plugin. "
                                "For a working example, please see the newer Conan 2.0 compatible "
                                "test package.")
            return
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self) or macos_shared(self):
            return
        for test in ["bigtable", "pubsub", "spanner", "speech", "storage"]:
            cmd = os.path.join("bin", test)
            self.run(cmd, run_environment=True)
