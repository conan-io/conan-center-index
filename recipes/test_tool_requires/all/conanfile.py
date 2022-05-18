from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout

# for bug: https://github.com/conan-io/conan/issues/11287

class TestToolRequiresConan(ConanFile):
    name = "test_tool_requires"
    version = "1.0"

    # Optional metadata
    license = "<Put the package license here>"
    url = "https://github.com/conan-io/conan-center-index"
    description = "<Description of TestToolRequires here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    homepage = "https://bugcity.com"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*"


    def requirements(self):
        self.requires("libcurl/7.80.0")
        self.requires("openssl/1.1.1o", override=True)

    def build_requirements(self):
        self.tool_requires("cmake/3.22.4")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def generate(self):
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
        self.cpp_info.libs = ["test_tool_requires"]
