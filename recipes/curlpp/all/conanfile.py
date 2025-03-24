from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, rm
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"

class CurlppConan(ConanFile):
    name = "curlpp"
    description = "C++ wrapper around libcURL"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jpbarrette/curlpp"
    topics = ("curl", "libcurl")
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

    @property
    def _min_cppstd(self):
        return 11

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
        # As it's a wrapper, it includes curl symbols in its public headers
        self.requires("libcurl/8.9.1", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        else:
            if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "6":
                raise ConanInvalidConfiguration("${self.ref} requires C++11. Please set 'compiler.cppstd=11'.")
            if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "14":
                raise ConanInvalidConfiguration("${self.ref} requires C++11. Please set 'compiler.cppstd=11'.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CURLPP_BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", os.path.join(self.source_folder, "doc"), os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "curlpp-config", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["libcurlpp" if is_msvc(self) and not self.options.shared else "curlpp"]

        self.cpp_info.set_property("cmake_file_name", "curlpp")
        self.cpp_info.set_property("cmake_target_name", "curlpp::curlpp")
