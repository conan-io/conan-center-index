from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=1.53.0"


class S2nConan(ConanFile):
    name = "s2n"
    description = "An implementation of the TLS/SSL protocols"
    topics = ("aws", "amazon", "cloud", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/s2n-tls"
    license = "Apache-2.0"
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

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/3.1.0")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Not supported (yet)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["UNSAFE_TREAT_WARNINGS_AS_ERRORS"] = False
        tc.variables["SEARCH_LIBCRYPTO"] = False # see CMakeLists wrapper
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "s2n"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "s2n")
        self.cpp_info.set_property("cmake_target_name", "AWS::s2n")
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["s2n-lib"].libs = ["s2n"]
        self.cpp_info.components["s2n-lib"].requires = ["openssl::crypto"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["s2n-lib"].system_libs = ["m", "pthread"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "s2n"
        self.cpp_info.filenames["cmake_find_package_multi"] = "s2n"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["s2n-lib"].names["cmake_find_package"] = "s2n"
        self.cpp_info.components["s2n-lib"].names["cmake_find_package_multi"] = "s2n"
        self.cpp_info.components["s2n-lib"].set_property("cmake_target_name", "AWS::s2n")
