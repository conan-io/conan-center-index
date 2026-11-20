from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.0.9"


class KavelConan(ConanFile):
    name = "kavel"
    description = "Generate AI images from C++ with no API key, using the Kavel image API"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.kavel.ai"
    topics = ("ai", "image-generation", "http", "api-client")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libcurl/[>=7.78 <9]")
        self.requires("nlohmann_json/3.11.3")

    def validate(self):
        check_min_cppstd(self, 17)
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} does not export symbols for a Windows DLL")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["KAVEL_BUILD_EXAMPLES"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["kavel"]
        self.cpp_info.set_property("cmake_file_name", "kavel")
        self.cpp_info.set_property("cmake_target_name", "kavel::kavel")
