from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.52.0"

class AwsCIO(ConanFile):
    name = "aws-c-io"
    description = "IO and TLS for application protocols"
    license = "Apache-2.0",
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-io"
    topics = ("aws", "amazon", "cloud", "io", "tls",)
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # the versions of aws-c-common and aws-c-io are tied since aws-c-common/0.6.12 and aws-c-io/0.10.10
        # Please refer https://github.com/conan-io/conan-center-index/issues/7763
        if Version(self.version) <= "0.10.9":
            self.requires("aws-c-common/0.6.11")
            self.requires("aws-c-cal/0.5.11")
        else:
            self.requires("aws-c-common/0.8.2")
            self.requires("aws-c-cal/0.5.13")

        if self.settings.os in ["Linux", "FreeBSD", "Android"]:
            self.requires("s2n/1.3.15")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
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
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-io"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-c-io")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-io")
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["aws-c-io-lib"].libs = ["aws-c-io"]
        if self.settings.os == "Macos":
            self.cpp_info.components["aws-c-io-lib"].frameworks.append("Security")
        if self.settings.os == "Windows":
            self.cpp_info.components["aws-c-io-lib"].system_libs = ["crypt32", "secur32", "shlwapi"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "aws-c-io"
        self.cpp_info.filenames["cmake_find_package_multi"] = "aws-c-io"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["aws-c-io-lib"].names["cmake_find_package"] = "aws-c-io"
        self.cpp_info.components["aws-c-io-lib"].names["cmake_find_package_multi"] = "aws-c-io"
        self.cpp_info.components["aws-c-io-lib"].set_property("cmake_target_name", "AWS::aws-c-io")
        self.cpp_info.components["aws-c-io-lib"].requires = ["aws-c-cal::aws-c-cal-lib", "aws-c-common::aws-c-common-lib"]
        if self.settings.os in ["Linux", "FreeBSD", "Android"]:
            self.cpp_info.components["aws-c-io-lib"].requires.append("s2n::s2n-lib")
