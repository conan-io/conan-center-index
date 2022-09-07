from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    @property
    def _with_netssl(self):
        return (
            ("enable_netssl" in self.dependencies["poco"].options and self.dependencies["poco"].options.enable_netssl) or
            ("enable_netssl_win" in self.dependencies["poco"].options and self.dependencies["poco"].options.enable_netssl_win)
        )

    @property
    def _with_encodings(self):
        return "enable_encodings" in self.dependencies["poco"].options and self.dependencies["poco"].options.enable_encodings

    @property
    def _with_jwt(self):
        return "enable_jwt" in self.dependencies["poco"].options and self.dependencies["poco"].options.enable_jwt

    @property
    def _with_prometheus(self):
        return "enable_prometheus" in self.dependencies["poco"].options and self.dependencies["poco"].options.enable_prometheus

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TEST_CRYPTO"] = self.dependencies["poco"].options.enable_crypto
        tc.variables["TEST_UTIL"] = self.dependencies["poco"].options.enable_util
        tc.variables["TEST_NET"] = self.dependencies["poco"].options.enable_net
        tc.variables["TEST_NETSSL"] = self._with_netssl
        tc.variables["TEST_SQLITE"] = self.dependencies["poco"].options.enable_data_sqlite
        tc.variables["TEST_ENCODINGS"] = self._with_encodings
        tc.variables["TEST_JWT"] = self._with_jwt
        tc.variables["TEST_PROMETHEUS"] = self._with_prometheus
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            if self.options["poco"].enable_util:
                self.run(os.path.join(self.cpp.build.bindirs[0], "util"), env="conanrun")
            if self.options["poco"].enable_crypto:
                self.run("{} {}".format(os.path.join(self.cpp.build.bindirs[0], "crypto"), os.path.join(self.source_folder, "conanfile.py")), env="conanrun")
            if self.options["poco"].enable_net:
                self.run(os.path.join(self.cpp.build.bindirs[0], "net"), env="conanrun")
                if self.options["poco"].enable_util:
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
