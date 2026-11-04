from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.tools.microsoft import is_msvc
from conan.tools.files import copy, get
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os


class TcpcatConan(ConanFile):
    name = "ydcpp-tcpcat"

    # Optional metadata
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ydcpp/tcpcat"
    description = "Simple C++ TCP Server and Client library."
    topics = ("network", "tcp", "tcp-server", "tcp-client")

    # Binary configuration
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "16",
            "msvc": "192",
            "clang": "7",
            "apple-clang": "12"
        }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        
        # Upstream meant to support Windows Shared builds, but they don't currently export any symbols
        # Disable for now until fixed. As this is an upstream issue they want fixed, we don't set
        # package_type = "static-library" in the configure() method so that users have a clear message error for now
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} does not currently support Windows shared builds due to an upstream issue")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def requirements(self):
        self.requires("asio/1.30.2", transitive_headers = True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ydcpp-tcpcat"]
        self.cpp_info.set_property("cmake_target_name", "ydcpp-tcpcat")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.append("m")
