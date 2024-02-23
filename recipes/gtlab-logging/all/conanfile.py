from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools import files
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
from conan import ConanFile
import os

required_conan_version = ">=1.59.0"

class GTLabLoggingConan(ConanFile):
    name = "gtlab-logging"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dlr-gtlab/gt-logging"
    topics = ("logging", "qt")
    description = "Simple logging interface with qt support"

    settings = "os", "arch", "compiler", "build_type"
    
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_qt": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_qt": False
    }

    def requirements(self):
        if self.options.with_qt:
            self.requires("qt/[>=5.0.0]")


    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _minimum_compilers_version(self):
        return {
            "14": {
                "Visual Studio": "15",
                "msvc": "191",
                "gcc": "7.3.1",
                "clang": "6",
                "apple-clang": "12",
            },
        }.get(self._min_cppstd, {})

    def validate(self):
        """
        Adapted from the gtest recipe

        Make sure that C++ 14 is available
        """

        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        compiler = self.settings.compiler
        min_version = self._minimum_compilers_version.get(str(compiler))
        if min_version and loose_lt_semver(str(compiler.version), min_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def generate(self):
        CMakeToolchain(self).generate()
        CMakeDeps(self).generate()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self.source_folder)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()


    def package(self):
        cmake = CMake(self)
        cmake.install()

        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        files.copy(self, "README.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        files.copy(self, os.path.join("LICENSES", "BSD-3-Clause.txt"), dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = ["GTlabLogging"] if self.settings.build_type != "Debug" else ["GTlabLogging-d"]
        
        self.cpp_info.includedirs.append(os.path.join("include", "logging"))

        self.cpp_info.libdirs = [os.path.join("lib", "logging")]

        self.cpp_info.set_property("cmake_file_name", "GTlabLogging")
        self.cpp_info.set_property("cmake_target_name", "GTlab::Logging")

        if self.options.with_qt:
            self.cpp_info.defines = ['GT_LOG_USE_QT_BINDINGS']
