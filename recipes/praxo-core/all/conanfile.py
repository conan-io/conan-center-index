from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy
import os


class PraxoCoreConan(ConanFile):
    name = "praxo-core"
    description = "Embeddable C agent runtime with policy, tools, streaming, and plugin hosts"
    license = "MIT"
    homepage = "https://github.com/axisvela/praxo-core"
    url = "https://github.com/axisvela/praxo-core"
    topics = ("agents", "agent-runtime", "llm", "tool-calling", "embedding")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="language/c")
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["praxo_core"]
        self.cpp_info.set_property("cmake_file_name", "praxo-core")
        self.cpp_info.set_property("cmake_target_name", "praxo::praxo_core")
