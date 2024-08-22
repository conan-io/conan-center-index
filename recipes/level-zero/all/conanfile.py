from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get


class LevelZeroConan(ConanFile):
    name = "level-zero"
    # version = "1.17.28"
    package_type = "library"

    # Optional metadata
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://spec.oneapi.io/level-zero/latest/core/INTRO.html"
    description = "oneAPI Level Zero Specification Headers and Loader"
    topics = ("api-headers", "loader", "level-zero", "oneapi")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def validate_build(self):
        if not self.options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support static build")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def source(self):
        version_data = self.conan_data["sources"][self.version]
        get(self, **version_data, strip_root=True)

    def layout(self):
        cmake_layout(self)
    
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
        self.cpp_info.libs = ["ze_loader"]
        self.cpp_info.includedirs = ["include", "include/level_zero"]

