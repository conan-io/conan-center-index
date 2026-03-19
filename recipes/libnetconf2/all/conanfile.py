from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import get


required_conan_version = ">=2.1"


class LibNetconf2Conan(ConanFile):
    name = "libnetconf2"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    description = "NETCONF client/server library"
    homepage = "https://github.com/CESNET/libnetconf2"
    topics = ("yang", "netconf")
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    languages = "C"
    implements = ["auto_shared_fpic"]
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {
        "shared": False,
        "fPIC": True
    }

    def requirements(self):
        self.requires("libyang/4.2.2")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("libssh/[>=0.10.6 <0.12]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ENABLE_EXAMPLES"] = False
        tc.cache_variables["ENABLE_TESTS"] = False
        tc.cache_variables["ENABLE_VALGRIND_TESTS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["netconf2"]
        self.cpp_info.set_property("cmake_file_name", "LibNETCONF2")
