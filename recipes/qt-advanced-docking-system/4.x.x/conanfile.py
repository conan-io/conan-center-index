from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get

class qt_advanced_docking_systemRecipe(ConanFile):
    name = "qt-advanced-docking-system"
    package_type = "library"

    # Optional metadata
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/githubuser0xFFFF/Qt-Advanced-Docking-System"
    description = (
        "Qt Advanced Docking System lets you create customizable layouts "
        "using a full featured window docking system similar to what is found "
        "in many popular integrated development environments (IDEs) such as "
        "Visual Studio."
    )
    topics = ("qt", "gui")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "qt_from_conan": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "qt_from_conan": False}

    def requirements(self):
        if self.options.qt_from_conan:
            self.requires("qt/[>=5.15]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

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
        cmake.configure(variables={
            "ADS_VERSION": self.version,
            "BUILD_EXAMPLES": False,
            "BUILD_STATIC" : not self.options.shared})
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        name = "qt6advanceddocking"
        if self.settings.build_type == "Debug":
            name += "d"
        if not self.options.shared:
            name += "_static"
        self.cpp_info.libs = [name]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs=["xcb"]
