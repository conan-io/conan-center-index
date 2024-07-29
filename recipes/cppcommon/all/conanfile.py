from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class CppCommon(ConanFile):
    name = "cppcommon"
    description = "C++ Common Library contains reusable components and patterns" \
        " for error and exceptions handling, filesystem manipulations, math," \
        " string format and encoding, shared memory, threading, time management" \
        " and others."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/chronoxor/CppCommon"
    topics = ("utils", "filesystem", "uuid", "synchronization", "queue")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": 10,
            "clang": 6,
            "gcc": 7,
            "Visual Studio": 16,
            "msvc": 192,
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) < "1.0.3" or self.version == "cci.20201104":
            self.requires("fmt/8.1.1", transitive_headers=True)
        else:
            self.requires("fmt/10.2.0", transitive_headers=True)
        if self.settings.os == "Linux":
            self.requires("util-linux-libuuid/2.39.2", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if is_msvc(self) and self.settings.arch == "x86":
            raise ConanInvalidConfiguration("Visual Studio x86 builds are not supported.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CPPCOMMON_MODULE"] = False
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()
        dpes = CMakeDeps(self)
        dpes.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
        copy(self, pattern="*.inl", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include", "plugins"), src=os.path.join(self.source_folder, "plugins"))

    def package_info(self):
        self.cpp_info.libs = ["cppcommon", "plugin-function", "plugin-interface"]
        self.cpp_info.includedirs.append(os.path.join(self.package_folder, "include", "plugins"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "rt", "dl", "m"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["userenv", "rpcrt4"]
