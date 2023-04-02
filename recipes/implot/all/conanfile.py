from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy
import os

required_conan_version = ">=1.59"

class ImplotConan(ConanFile):
    name = "implot"

    package_type = "library"

    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/epezent/implot"
    description = "Advanced 2D Plotting for Dear ImGui"
    topics = ("imgui", "plot", "graphics", )
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = ["CMakeLists.txt"]

    options = {
        "shared": [True, False],
         "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "src")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("imgui/1.89.4", transitive_headers=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self._source_subfolder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["implot"]
