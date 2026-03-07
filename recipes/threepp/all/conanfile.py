from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.scm import Git


class ThreeppRecipe(ConanFile):
    name = "threepp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/markaren/threepp"
    description = (
        "Cross-platform C++20 port of the popular Javascript 3D library three.js"
    )
    topics = ("threejs", "opengl", "3d-graphics")
    package_type = "library"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {"shared": False, "fPIC": True}

    def package_info(self):
        self.cpp_info.libs = ["threepp"]

    def layout(self):
        cmake_layout(self)

    def source(self):
        git = Git(self)
        entry = self.conan_data["sources"][self.version]
        git.clone(url=entry["url"], target=".")
        git.checkout(commit=entry["commit"])

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["THREEPP_BUILD_TESTS"] = False
        tc.variables["THREEPP_BUILD_EXAMPLES"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
