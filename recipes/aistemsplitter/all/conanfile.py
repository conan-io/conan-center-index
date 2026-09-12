import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=2.0"


class AistemsplitterConan(ConanFile):
    name = "aistemsplitter"
    description = "Official C++ SDK for the AIStemSplitter public API"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aistemsplitter/aistemsplitter-cpp"
    topics = ("aistemsplitter", "audio", "stem-separation", "sdk")

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libcurl/8.19.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

        minimum_version = {
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
            "msvc": "191",
            "Visual Studio": "15",
        }.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++17, which your compiler does not support"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["AISTEMSPLITTER_BUILD_TESTS"] = False
        tc.cache_variables["AISTEMSPLITTER_BUILD_EXAMPLES"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aistemsplitter")
        self.cpp_info.set_property("cmake_target_name", "aistemsplitter::aistemsplitter")
        self.cpp_info.set_property("pkg_config_name", "aistemsplitter")
        self.cpp_info.libs = ["aistemsplitter"]
        self.cpp_info.requires = ["libcurl::libcurl"]
