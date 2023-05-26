from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
import os

required_conan_version = ">=1.53.0"

class mailioConan(ConanFile):
    name = "mailio"
    description = "mailio is a cross platform C++ library for MIME format and SMTP, POP3 and IMAP protocols."
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/karastojko/mailio"
    topics = ("smtp", "imap", "email", "mail", "libraries", "cpp")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False
    }
    short_paths = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compiler_required_cpp(self): 
        return {
            "gcc": "8.3",
            "clang": "6",
            "Visual Studio": "15",
            "msvc": "191",
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.81.0")
        self.requires("openssl/1.1.1s")

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        try:
            minimum_required_compiler_version = self._compiler_required_cpp[str(self.settings.compiler)]
            if Version(self.settings.compiler.version) < minimum_required_compiler_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires c++{self._min_cppstd} support. The current compiler does not support it.")
        except KeyError:
            self.output.warn(f"{self.ref} has no support for the current compiler. Please consider adding it.")


    def build_requirements(self):
        # mailio requires cmake >= 3.16.3
        self.tool_requires("cmake/[>=3.16.3 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MAILIO_BUILD_SHARED_LIBRARY"] = self.options.shared
        tc.variables["MAILIO_BUILD_DOCUMENTATION"] = False
        tc.variables["MAILIO_BUILD_EXAMPLES"] = False
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
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["mailio"]
        self.cpp_info.requires = ["boost::system", "boost::date_time", "boost::regex", "openssl::openssl"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
