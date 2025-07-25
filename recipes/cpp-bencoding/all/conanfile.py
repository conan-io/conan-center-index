from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get


class cpp_bencodingRecipe(ConanFile):
    name = "cpp-bencoding"
    version = "0.1"
    package_type = "library"

    # Optional metadata
    license = "MIT"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "A C++ bencoding library supporting both decoding and encoding"
    topics = ("bittorrent", "torrent", "bencoding")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "with_tests": [True, False]}
    default_options = {"shared": False, "fPIC": True, "with_tests": False}

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)
    
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["bencoding"]
        self.cpp_info.set_property("cmake_file_name", "bencoding")
        self.cpp_info.set_property("cmake_target_name", f"bencoding::bencoding")
        self.cpp_info.set_property("pkg_config_name",  "bencoding")

