from conan import ConanFile
from conan.tools.build import build_jobs, can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import chdir


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
        tc.variables["TEST_NET"] = poco_options.enable_net
        tc.variables["TEST_NETSSL"] = poco_options.get_safe("enable_netssl") or poco_options.get_safe("enable_netssl_win")
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
            with chdir(self, self.build_folder):
                self.run(f"ctest --output-on-failure -C {self.settings.build_type} -j {build_jobs(self)}", env="conanrun")
