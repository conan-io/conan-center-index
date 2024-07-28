from conan import ConanFile
from conan.tools.files import get, collect_libs
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain

class NodeEditorConan(ConanFile):
    name = "nodeeditor"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/paceholder/nodeeditor"
    topics = ("qt", "ui", "dataflow")
    settings = "os", "compiler", "arch", "build_type"

    options = {"shared" : [True, False]}
    default_options = {"shared" : False}
    package_type = "library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("qt/6.7.1")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_DOCS"] = False
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.generate()

    def build(self):
        cm = CMake(self)
        cm.configure()
        cm.build()

    def package(self):
        cm = CMake(self)
        cm.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.set_property("cmake_find_mode", "config")
        self.cpp_info.set_property("cmake_target_name", "QtNodes::QtNodes")
        
