from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy
import os


class NekoSystemConan(ConanFile):
    name = "neko-system"
    version = "1.0.1"
    license = "MIT OR Apache-2.0"
    author = "moehoshio"
    url = "https://github.com/moehoshio/NekoSystem"
    description = "A cross-platform C++20 system information library providing memory information, platform detection, and system utilities. "
    topics = ("cpp", "system", "information", "library", "cross-platform", "module-support", "neko", "memory", "platform", "utilities")
    
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "enable_module": [True, False]

    }
    default_options = {
        "enable_module": False
    }
    
    package_type = "static-library"

    exports_sources = "CMakeLists.txt", "include/*", "src/*", "tests/*", "cmake/*", "LICENSE", "README.md"
    
    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NEKO_SYSTEM_BUILD_TESTS"] = False
        tc.variables["NEKO_SYSTEM_ENABLE_MODULE"] = self.options.enable_module
        # Automatically fetch NekoSchema and NekoFunction until it is available in Conan
        tc.variables["NEKO_SYSTEM_AUTO_FETCH_DEPS"] = True
        tc.variables["NEKO_SCHEMA_BUILD_TESTS"] = False
        tc.variables["NEKO_FUNCTION_BUILD_TESTS"] = False
        tc.generate()
        
        deps = CMakeDeps(self)
        deps.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.cppm", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        
        cmake = CMake(self)
        cmake.install()
    
    def package_info(self):
        # Set the CMake package file name to match the official CMake config
        self.cpp_info.set_property("cmake_file_name", "NekoSystem")
        
        # Main target
        self.cpp_info.components["NekoSystem"].set_property("cmake_target_name", "Neko::System")
        self.cpp_info.components["NekoSystem"].includedirs = ["include"]
        # Library target with compiled code
        # Note: Library will be installed via cmake.install() in package()
        lib_folder = os.path.join(self.package_folder, "lib")
        if os.path.exists(lib_folder):
            self.cpp_info.components["NekoSystem"].libs = ["NekoSystem"]
        
        # Module support (if enabled)
        if self.options.enable_module:
            self.cpp_info.components["NekoFunctionModule"].set_property("cmake_target_name", "Neko::Function::Module")
            self.cpp_info.components["NekoFunctionModule"].includedirs = ["include"]
            self.cpp_info.components["NekoFunctionModule"].requires = ["NekoFunction"]
    
    def package_id(self):
        self.info.clear()
