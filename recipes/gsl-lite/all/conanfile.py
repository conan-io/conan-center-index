import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.1"


class GslLiteConan(ConanFile):
    name = "gsl-lite"
    description = "ISO C++ Core Guidelines Library implementation for C++98, C++11 up"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gsl-lite/gsl-lite"
    topics = ("GSL", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    #  There are three configuration options for this GSL implementation's behavior
    #  when pre/post conditions on the GSL types are violated:
    #
    #  1. GSL_TERMINATE_ON_CONTRACT_VIOLATION: std::terminate will be called (default)
    #  2. GSL_THROW_ON_CONTRACT_VIOLATION: a gsl::fail_fast exception will be thrown
    #  3. GSL_UNENFORCED_ON_CONTRACT_VIOLATION: nothing happens
    #
    options = {
        "on_contract_violation": ["terminate", "throw", "unenforced"]
    }
    default_options = {
        "on_contract_violation": "terminate",
    }

    @property
    def _contract_map(self):
        return {
            "terminate": "GSL_TERMINATE_ON_CONTRACT_VIOLATION",
            "throw": "GSL_THROW_ON_CONTRACT_VIOLATION",
            "unenforced": "GSL_UNENFORCED_ON_CONTRACT_VIOLATION"
        }

    def config_options(self):
        if Version(self.version) >= "1.0":
            del self.options.on_contract_violation

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",  src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "gsl-lite")
        self.cpp_info.set_property("cmake_target_name", "gsl-lite::gsl-lite")
        self.cpp_info.set_property("cmake_target_aliases", ["gsl::gsl-lite"])

        self.cpp_info.set_property("cmake_config_version_compat", "SameMajorVersion")

        if Version(self.version) < "1.0":
            # Don't define a cmake target for versions >= 1.0
            # the old versions might expect it so keep it
            self.cpp_info.components["gsllite"].defines = [self._contract_map[str(self.options.on_contract_violation)]]
            self.cpp_info.components["gsllite"].bindirs = []
            self.cpp_info.components["gsllite"].libdirs = []
