from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get
from conan.tools.gnu import PkgConfigDeps

class libjwtRecipe(ConanFile):
    name = "libjwt"
    version = "1.18.3"
    package_type = "library"

    # Optional metadata
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of libjwt package here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def source(self):
        get(self, 'https://github.com/benmcollins/libjwt/archive/refs/tags/v1.18.3.zip', strip_root=True)

    def requirements(self):
        self.requires("jansson/2.14")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        cmakeDeps = CMakeDeps(self)
        # cmakeDeps.set_property("jansson", "pkg_config_name", "jansson")
        # cmakeDeps.set_property("jansson", "cmake_file_name", "JANSSON")
        # cmakeDeps.set_property("jansson", "cmake_target_name", "PkgConfig::JANSSON")
        cmakeDeps.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def build_requirements(self):
        self.tool_requires("pkgconf/[>=2.2 <3]")

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["libjwt"]
        self.cpp_info.set_property("cmake_file_name", "libjwt")
        self.cpp_info.set_property("cmake_target_name", "libjwt::libjwt")
        # self.cpp_info.requires = ["jansson::jansson"]

        # self.cpp_info.components["jansson"].includedirs = ["include"]
        # self.cpp_info.components["libjansson-dev"].set_property("pkg_config_name", "jansson")
        # self.cpp_info.components["libjansson-dev"].set_property("pkg_config_aliases", ["jansson", "Jansson"])
