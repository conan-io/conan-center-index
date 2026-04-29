import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir

required_conan_version = ">=2.0.9"


class SwaggerCppRecipe(ConanFile):
    name = "swaggercpp"
    description = "Professional C++23 library for Swagger/OpenAPI parsing, validation, traversal, and serialization."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/stescobedo92/swagger-cpp"
    topics = ("swagger", "openapi", "openapi3", "rest", "json", "yaml")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpp-httplib/0.39.0", visible=False)
        self.requires("nlohmann_json/3.12.0", transitive_headers=True)
        self.requires("yaml-cpp/0.9.0", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 23)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        toolchain = CMakeToolchain(self)
        toolchain.variables["SWAGGERCPP_BUILD_TESTS"] = False
        toolchain.variables["SWAGGERCPP_BUILD_BENCHMARKS"] = False
        toolchain.variables["SWAGGERCPP_BUILD_EXAMPLES"] = False
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["swaggercpp"]
        self.cpp_info.set_property("cmake_file_name", "swaggercpp")
        self.cpp_info.set_property("cmake_target_name", "swaggercpp::swaggercpp")
        self.cpp_info.set_property("pkg_config_name", "swaggercpp")
