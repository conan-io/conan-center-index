from conan import ConanFile, tools
from conan.tools.cmake import CMake, cmake_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
import os

required_conan_version = ">=1.43.0"

class HsmConan(ConanFile):
    name = "erikzenker-hsm"
    license = "MIT"
    homepage = "https://github.com/erikzenker/hsm.git"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The hana state machine (hsm) is a finite state machine library based on the boost hana meta programming library. It follows the principles of the boost msm and boost sml libraries, but tries to reduce own complex meta programming code to a minimum."
    topics = ("state-machine", "template-meta-programming")
    requires = "boost/1.79.0"
    no_copy_source = True
    settings = "os", "arch", "build_type", "compiler"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        cmake_layout(self)

    def validate(self):
        # https://github.com/erikzenker/hsm#dependencies
        if self.settings.compiler == "clang" and Version(str(self.settings.compiler.version)) < '8':
            raise ConanInvalidConfiguration("clang 8+ is required")
        if self.settings.compiler == "gcc" and Version(str(self.settings.compiler.version)) < '8':
            raise ConanInvalidConfiguration("GCC 8+ is required")

    def source(self):
        tools.files.get(**self.conan_data["sources"][self.version], conanfile=self, destination=self.source_folder, strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        cmake = CMake(self) 
        cmake.install()
        tools.files.rmdir(conanfile=self, path=os.path.join(self.package_folder, "lib", "cmake"))
        self.copy("LICENSE", src=self.source_folder, dst="licenses")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "hsm"
        self.cpp_info.names["cmake_find_package_multi"] = "hsm"
        self.cpp_info.set_property("cmake_file_name", "hsm")
        self.cpp_info.set_property("cmake_target_name", "hsm::hsm")
