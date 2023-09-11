from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc_static_runtime
import os

required_conan_version = ">=1.53.0"

class OctoEncryptionCPPConan(ConanFile):
    name = "octo-encryption-cpp"
    description = "Octo encryption library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ofiriluz/octo-encryption-cpp"
    topics = ("cryptography", "cpp")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "9",
            "apple-clang": "11",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]", transitive_headers=True)

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if self.settings.compiler == "clang" and self.settings.compiler.get_safe("libcxx") == "libc++":
            raise ConanInvalidConfiguration(f"{self.name} does not support clang with libc++. Use libstdc++ instead.")
        if is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(f"{self.ref} does not support MSVC MT/MTd configurations, only MD/MDd is supported")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DISABLE_TESTS"] = True
        tc.variables["DISABLE_EXAMPLES"] = True
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["octo-encryption-cpp"]

        self.cpp_info.set_property("cmake_file_name", "octo-encryption-cpp")
        self.cpp_info.set_property("cmake_target_name", "octo::octo-encryption-cpp")
        self.cpp_info.set_property("pkg_config_name", "octo-encryption-cpp")
        self.cpp_info.requires = ["openssl::openssl"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "octo-encryption-cpp"
        self.cpp_info.names["cmake_find_package_multi"] = "octo-encryption-cpp"
        self.cpp_info.names["pkg_config"] = "octo-encryption-cpp"
