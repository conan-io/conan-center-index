from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=1.53.0"

class MicroserviceEssentials(ConanFile):
    name = "microservice-essentials"    
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/seboste/microservice-essentials"
    license = "MIT"    
    description = """microservice-essentials is a portable, independent C++ library that takes care of typical recurring concerns that occur in microservice development."""
    topics = ("microservices", "cloud-native", "request-handling")
    settings = "os", "compiler", "arch", "build_type"    
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tests": [True, False],
        "with_examples": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tests": False,
        "with_examples": False
    }

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
            "Visual Studio": "15.7",
            "msvc": "191",
        }

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16.3 <4]")

    def requirements(self):
        if self.options.with_examples:
            self.requires("cpp-httplib/0.14.1")
            self.requires("nlohmann_json/3.11.2")
            self.requires("openssl/[>=3 <4]")
            self.requires("grpc/1.54.3")
        if self.options.with_tests:
            self.requires("catch2/3.4.0")
            self.requires("nlohmann_json/3.11.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["BUILD_TESTING"] = self.options.with_tests
        tc.variables["BUILD_EXAMPLES"] = self.options.with_examples
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "17")

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                "{} requires C++17, which your compiler does not support.".format(self.name)
            )
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
 
    def package_info(self):
        self.cpp_info.libs = ["microservice-essentials"]
        self.cpp_info.bindirs.extend(["lib"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
