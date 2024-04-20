import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get
from conan.tools.scm import Version

required_conan_version = ">=1.60.0 <2 || >=2.0.5"


class DaggyConan(ConanFile):
    name = "daggy"
    description = "Data Aggregation Utility and C/C++ developer library for data streams catching"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/synacker/daggy"
    topics = ("streaming", "qt", "monitoring", "process", "stream-processing", "extensible",
              "serverless-framework", "aggregation", "ssh2", "cross-platform", "ssh-client")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssh2": [True, False],
        "with_yaml": [True, False],
        "with_console": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssh2": True,
        "with_yaml": True,
        "with_console": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "8",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["qt"].shared = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Qt is used in the public headers
        self.requires("qt/6.6.2", transitive_headers=True, transitive_libs=True)
        self.requires("kainjow-mustache/4.1")
        if self.options.with_yaml:
            self.requires("yaml-cpp/0.8.0")
        if self.options.with_ssh2:
            self.requires("libssh2/1.11.0")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if not self.dependencies["qt"].options.shared:
            raise ConanInvalidConfiguration("Shared Qt lib is required.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21 <4]")
        self.tool_requires("qt/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        # Required for Qt's moc
        env = VirtualRunEnv(self)
        env.generate(scope="build")

        tc = CMakeToolchain(self)
        tc.variables["SSH2_SUPPORT"] = self.options.with_ssh2
        tc.variables["YAML_SUPPORT"] = self.options.with_yaml
        tc.variables["CONSOLE"] = self.options.with_console
        tc.variables["PACKAGE_DEPS"] = False
        tc.variables["VERSION"] = self.version
        tc.variables["CONAN_BUILD"] = True
        tc.variables["BUILD_TESTING"] = False
        if self.options.shared:
            tc.variables["CMAKE_C_VISIBILITY_PRESET"] = "hidden"
            tc.variables["CMAKE_CXX_VISIBILITY_PRESET"] = "hidden"
            tc.variables["CMAKE_VISIBILITY_INLINES_HIDDEN"] = 1
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "src"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["DaggyCore"]
