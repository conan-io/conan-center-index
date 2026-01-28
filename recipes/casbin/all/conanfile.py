from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file, rename
from conan.tools.scm import Version
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
    languages = "C++"

    @property
    def _min_cppstd(self):
        return 17

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("nlohmann_json/[>=3.11 <3.13]", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CASBIN_BUILD_TEST"] = False
        tc.cache_variables["CASBIN_BUILD_BENCHMARK"] = False
        tc.cache_variables["CASBIN_BUILD_PYTHON_BINDINGS"] = False
        tc.cache_variables["CASBIN_INSTALL"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        replace_in_file(
            self,
            os.path.join(self.source_folder, "cmake", "modules", "FindExtPackages.cmake"),
            "find_package(json 3.10.1 REQUIRED)",
            "find_package(nlohmann_json REQUIRED)"
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

        # Upstream does not install these so we manually copy them
        copy(self, "*.h", os.path.join(self.source_folder, "include"),
             os.path.join(self.package_folder, "include"))
        copy(self, "*.hpp", os.path.join(self.source_folder, "include"),
             os.path.join(self.package_folder, "include"))
        lib_folder = os.path.join(self.package_folder, "lib")
        copy(self, "*.a", self.build_folder, lib_folder, keep_path=False)
        copy(self, "*.lib", self.build_folder, lib_folder, keep_path=False)

        # Prepend lib prefix
        if self.settings.os != "Windows":
            casbin_lib = os.path.join(lib_folder, "casbin.a")
            if os.path.exists(casbin_lib):
                rename(self, casbin_lib, os.path.join(lib_folder, "libcasbin.a"))

    def package_info(self):
        self.cpp_info.libs = ["casbin"]
        self.cpp_info.set_property("cmake_file_name", "casbin")
        self.cpp_info.set_property("cmake_target_name", "casbin::casbin")
        self.cpp_info.requires = ["nlohmann_json::nlohmann_json"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
