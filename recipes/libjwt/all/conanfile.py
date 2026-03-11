from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, replace_in_file, rmdir
import os

required_conan_version = ">=2.4"
class libjwtRecipe(ConanFile):
    name = "libjwt"
    package_type = "library"
    license = "MPL-2.0"
    homepage = "https://github.com/benmcollins/libjwt"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The C JSON Web Token Library +JWK +JWKS"
    topics = ("json", "jwt", "jwt-token")

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    languages = "C"
    implements = ["auto_shared_fpic"]

    def source(self):
        get(self, self.conan_data["sources"][self.version]["url"], strip_root=True)
        replace_in_file(
            self, os.path.join(self.source_folder, "libjwt", "CMakeLists.txt"),
            "PKG_SEARCH_MODULE( JANSSON jansson )",
            "find_package(jansson REQUIRED CONFIG)")

    def requirements(self):
        self.requires("openssl/[>=3 <4]")
        self.requires("jansson/[>=2 <3]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["USE_INSTALLED_JANSSON"] = True
        tc.cache_variables["ENABLE_PIC"] = False # let Conan handle it via the toolchain
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.generate()

        cmakeDeps = CMakeDeps(self)
        cmakeDeps.set_property("jansson", "cmake_target_name", "jansson")
        cmakeDeps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "LICENSE", self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "libjwt")) # cmake configs

    def package_info(self):
        self.cpp_info.libs = ["jwt"]
