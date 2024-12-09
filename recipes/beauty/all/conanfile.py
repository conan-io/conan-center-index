from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class BeautyConan(ConanFile):
    name = "beauty"
    description = "HTTP Server above Boost.Beast"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dfleury2/beauty"
    topics = ("http", "server", "boost.beast")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
    }

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "Visual Studio": "16",
            "msvc": "192",
            "apple-clang": "10"
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
        # beauty public headers include some boost headers.
        # For example beauty/application.hpp includes boost/asio.hpp
        if Version(self.version) >= "1.0.4":
            # https://github.com/dfleury2/beauty/issues/30
            self.requires("boost/1.85.0", transitive_headers=True)
        else:
            self.requires("boost/1.84.0", transitive_headers=True)
        if self.options.with_openssl:
            # dependency of asio in boost, exposed in boost/asio/ssl/detail/openssl_types.hpp
            self.requires("openssl/[>=1.1 <4]", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.settings.compiler == "clang" and self.settings.compiler.libcxx != "libc++":
            raise ConanInvalidConfiguration(f"{self.ref} clang compiler requires -s compiler.libcxx=libc++")

        if self.settings.compiler == "apple-clang" and self.options.shared:
            raise ConanInvalidConfiguration(f"The option {self.ref}:shared=True is not supported on Apple Clang. Use static instead.")

        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} shared=True is not supported with {self.settings.compiler}")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()
        tc = CMakeToolchain(self)
        tc.variables["CONAN"] = False
        tc.variables["BEAUTY_ENABLE_OPENSSL"] = self.options.with_openssl
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="beauty")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "beauty")
        self.cpp_info.set_property("cmake_target_name", "beauty::beauty")
        self.cpp_info.libs = ["beauty"]
        self.cpp_info.requires = ["boost::headers"]
        if self.options.with_openssl:
            self.cpp_info.requires.append("openssl::ssl")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["crypt32"]
        if self.options.with_openssl:
            self.cpp_info.defines = ["BEAUTY_ENABLE_OPENSSL"]
