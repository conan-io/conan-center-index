from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get


class portaudioRecipe(ConanFile):
    name = "portaudio"
    version = "19.7"
    package_type = "library"

    license = "MIT"
    url = "http://www.portaudio.com"
    description = "A free, cross-platform, open source, audio I/O library."
    topics = ("audio",)

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    #exports_sources = "CMakeLists.txt", "src/*", "include/*"
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
    
    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

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
        self.cpp_info.libs = ["portaudio"]

