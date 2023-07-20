import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class DaggyConan(ConanFile):
    name = "daggy"
    description = "Data Aggregation Utility and C/C++ developer library for data streams catching"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://daggy.dev"
    topics = ("streaming", "qt", "monitoring", "process", "stream-processing", "extensible", "serverless-framework", "aggregation", "ssh2", "crossplatform", "ssh-client")

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
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "8",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

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
        self.requires("qt/6.5.0")
        self.requires("kainjow-mustache/4.1")

        if self.options.with_yaml:
            self.requires("yaml-cpp/0.7.0")

        if self.options.with_ssh2:
            self.requires("libssh2/1.10.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warning(f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support.")
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++{} support. The current compiler {} {} does not support it.".format(
                        self.name,
                        self._minimum_cpp_standard,
                        self.settings.compiler,
                        self.settings.compiler.version,
                    )
                )

        if not self.dependencies["qt"].options.shared:
            raise ConanInvalidConfiguration("Shared Qt lib is required.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_CXX_STANDARD"] = 17
        tc.variables["CMAKE_CXX_STANDARD_REQUIRED"] = True
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
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"),
             keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["DaggyCore"]
