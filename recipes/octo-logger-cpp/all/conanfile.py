from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class OctoLoggerCPPConan(ConanFile):
    name = "octo-logger-cpp"
    description = "CPP Stream based logging library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ofiriluz/octo-logger-cpp"
    topics = ("logging", "stream", "syslog", "cloudwatch")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_aws": [True, False],
    }
    default_options = {
        "with_aws": False,
    }

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

    @property
    def _aws_supported(self):
        return Version(self.version) >= "1.2.0"

    def configure(self):
        if not self._aws_supported:
            del self.options.with_aws

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fmt/10.2.1", transitive_headers=True)
        if self.options.get_safe("with_aws"):
            self.requires("nlohmann_json/3.11.3")
            self.requires("aws-sdk-cpp/1.9.234")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if self.settings.compiler == "clang" and self.settings.compiler.get_safe("libcxx") == "libc++":
            raise ConanInvalidConfiguration(f"{self.ref} does not support clang with libc++. Use libstdc++ instead.")
        if is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration(f"{self.ref} does not support MSVC static runtime. Use dynamic runtime instead.")
        if self.options.get_safe("with_aws"):
            if not self.dependencies["aws-sdk-cpp"].options.logs:
                raise ConanInvalidConfiguration(f"{self.ref} requires the option aws-sdk-cpp:logs=True")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DISABLE_TESTS"] = True
        tc.variables["DISABLE_EXAMPLES"] = True
        if self.options.get_safe("with_aws"):
            tc.variables["WITH_AWS"] = True
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
        self.cpp_info.set_property("cmake_file_name", "octo-logger-cpp")
        self.cpp_info.set_property("cmake_target_name", "octo::octo-logger-cpp")
        self.cpp_info.libs = ["octo-logger-cpp"]
        self.cpp_info.requires = ["fmt::fmt"]
        if self.options.get_safe("with_aws"):
            self.cpp_info.requires.extend([
                "nlohmann_json::nlohmann_json",
                "aws-sdk-cpp::monitoring"
            ])
