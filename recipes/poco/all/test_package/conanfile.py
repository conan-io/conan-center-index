from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        poco_options = self.dependencies["poco"].options
        tc.variables["TEST_CRYPTO"] = poco_options.enable_crypto
        tc.variables["TEST_UTIL"] = poco_options.enable_util
        tc.variables["TEST_NET"] = False
        tc.variables["TEST_NETSSL"] = False
        tc.variables["TEST_SQLITE"] = poco_options.enable_data_sqlite
        tc.variables["TEST_ENCODINGS"] = poco_options.get_safe("enable_encodings", False)
        tc.variables["TEST_JWT"] = poco_options.get_safe("enable_jwt", False)
        tc.variables["TEST_PROMETHEUS"] = poco_options.get_safe("enable_prometheus", False)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            poco_options = self.dependencies["poco"].options
            if poco_options.enable_util:
                self.run(os.path.join(self.cpp.build.bindirs[0], "util"), env="conanrun")
            if poco_options.enable_crypto:
                self.run("{} {}".format(os.path.join(self.cpp.build.bindirs[0], "crypto"), os.path.join(self.source_folder, "conanfile.py")), env="conanrun")
            if False:
                if poco_options.enable_net:
                    self.run(os.path.join(self.cpp.build.bindirs[0], "net"), env="conanrun")
                    if poco_options.enable_util:
                        self.run(os.path.join(self.cpp.build.bindirs[0], "net_2"), env="conanrun")
                test_netssl = os.path.join(self.cpp.build.bindirs[0], "netssl")
                if os.path.exists(test_netssl):
                    self.run(test_netssl, env="conanrun")
            test_sqlite = os.path.join(self.cpp.build.bindirs[0], "sqlite")
            if os.path.exists(test_sqlite):
                self.run(test_sqlite, env="conanrun")
            test_encodings = os.path.join(self.cpp.build.bindirs[0], "encodings")
            if os.path.exists(test_encodings):
                self.run(test_encodings, env="conanrun")
            test_jwt = os.path.join(self.cpp.build.bindirs[0], "jwt")
            if os.path.exists(test_jwt):
                self.run(test_jwt, env="conanrun")
            test_prometheus = os.path.join(self.cpp.build.bindirs[0], "prometheus")
            if os.path.exists(test_prometheus):
                self.run(test_prometheus, env="conanrun")
