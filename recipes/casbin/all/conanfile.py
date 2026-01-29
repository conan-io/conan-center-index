from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file
import os

required_conan_version = ">=2.4.0"

class CasbinConan(ConanFile):
    name = "casbin"
    description = "An authorization library that supports access control models like ACL, RBAC, ABAC in C/C++"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/casbin/casbin-cpp"
    topics = ("authorization", "access-control", "acl", "rbac", "abac", "permission")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
      "fPIC": [True, False],
    }
    default_options = {
      "fPIC": True
    }
    languages = "C++"
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("nlohmann_json/[>=3.11 <3.13]", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD", "# set(CMAKE_CXX_STANDARD")
        replace_in_file(self, os.path.join(self.source_folder, "casbin", "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD", "# set(CMAKE_CXX_STANDARD")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CASBIN_BUILD_TEST"] = False
        tc.cache_variables["CASBIN_BUILD_BENCHMARK"] = False
        tc.cache_variables["CASBIN_BUILD_PYTHON_BINDINGS"] = False
        tc.cache_variables["CASBIN_INSTALL"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("nlohmann_json", "cmake_file_name", "json")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

        # Upstream does not install these so we manually copy them
        lib_folder = os.path.join(self.package_folder, "lib")
        copy(self, "*.a", self.build_folder, lib_folder, keep_path=False)
        copy(self, "*.lib", self.build_folder, lib_folder, keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["casbin"]
        else:
            self.cpp_info.libs = ["casbin.a"]
        self.cpp_info.set_property("cmake_file_name", "casbin")
        self.cpp_info.set_property("cmake_target_name", "casbin::casbin")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
