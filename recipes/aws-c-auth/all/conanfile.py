from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir
import os

required_conan_version = ">=2.4"


class AwsCAuth(ConanFile):
    name = "aws-c-auth"
    description = (
        "C99 library implementation of AWS client-side authentication: "
        "standard credentials providers and signing."
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-auth"
    topics = ("aws", "amazon", "cloud", "authentication", "credentials", "providers", "signing")
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
    languages = "C"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("aws-c-common/0.12.5", transitive_headers=True, transitive_libs=True)
        self.requires("aws-c-cal/0.9.8")
        # Are we overlinking? This has never been a requirement in upstream's CMakeLists.txt
        self.requires("aws-c-io/0.23.2", transitive_headers=True, transitive_libs=True)
        self.requires("aws-c-http/0.10.5", transitive_headers=True)
        self.requires("aws-c-sdkutils/0.2.4", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.cache_variables['AWS_STATIC_MSVC_RUNTIME_LIBRARY'] = self.settings.os == "Windows" and self.settings.get_safe("compiler.runtime") == "static"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-auth"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-auth")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-auth")
        self.cpp_info.libs = ["aws-c-auth"]
        if self.options.shared:
            self.cpp_info.defines.append("AWS_AUTH_USE_IMPORT_EXPORT")
