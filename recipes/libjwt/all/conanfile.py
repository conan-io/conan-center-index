from conan import ConanFile, conan_version
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get
from conan.tools.system import package_manager
from conan.tools.scm import Version


class libjwtRecipe(ConanFile):
    name = "libjwt"
    package_type = "library"

    # Optional metadata
    license = "Mozilla Public License Version 2.0"
    author = "Ben Collins"
    url = "https://github.com/benmcollins/libjwt"
    description = "The C JSON Web Token Library +JWK +JWKS"
    topics = ("json", "jwt", "jwt-token")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def source(self):
        get(self, self.conan_data["sources"][self.version]["url"], strip_root=True)

    def requirements(self):
        self.requires("openssl/3.3.2")
        self.requires("jansson/2.14")

    def system_requirements(self):
        apt = package_manager.Apt(self)
        apt.install(["libjansson-dev"], update=True, check=True)
        
        yum = package_manager.Yum(self)
        yum.install(["jansson-devel"], update=True, check=True)

        dnf = package_manager.Dnf(self)
        dnf.install(["jansson-devel"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["libjansson-devel"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["jansson"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install(["jansson"], update=True, check=True)
        
        if Version(conan_version) >= "2.0.10":
            alpine = package_manager.Apk(self)
            alpine.install(["jansson"], update=True, check=True)

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
        cmakeDeps.generate()

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
        self.cpp_info.libs = ["jwt"]
