from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, check_min_cstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=2.4"


class KleidiaiConan(ConanFile):
    name = "kleidiai"
    description = ("KleidiAI is an open-source library that provides optimized performance-critical routines, "
                  "also known as micro-kernels, for artificial intelligence (AI) workloads tailored for Arm CPUs.")
    license = "Apache-2.0 AND BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.arm.com/kleidi/kleidiai"
    topics = ("arm", "ai", "ml", "ai-acceleration", "micro-kernels", "compute-kernels")
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
    languages = ["C", "C++"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        # Windows ARM does not support (yet) shared builds
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.shared
            self.package_type = "static-library"

    def validate(self):
        check_min_cppstd(self, 17)
        if self.settings.get_safe("compiler.cstd"):
            check_min_cstd(self, 99)
        if "arm" not in self.settings.arch:
            raise ConanInvalidConfiguration("KleidiAI is an ARM project and only supports ARM architectures.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, "set(CMAKE_CXX_STANDARD 17)", "")
        replace_in_file(self, cmakelists, "set(CMAKE_C_STANDARD 99)", "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["KLEIDIAI_BUILD_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*", os.path.join(self.source_folder, "LICENSES"), os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["kleidiai"]
        self.cpp_info.set_property("cmake_file_name", "KleidiAI")
        self.cpp_info.set_property("cmake_target_name", "KleidiAI::kleidiai")
        # Library public definitions
        if is_msvc(self):
            self.cpp_info.defines.append("KLEIDIAI_HAS_BUILTIN_ASSUME0")
        elif self.settings.compiler in ("clang", "apple-clang", "gcc"):
            self.cpp_info.defines.append("KLEIDIAI_HAS_BUILTIN_UNREACHABLE")
