from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get, copy
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"

class AzureSDKForCppConan(ConanFile):
    name = "azure-sdk-for-cpp"
    description = "Microsoft Azure Storage Client Library for C++"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Azure/azure-sdk-for-cpp"
    topics = ("azure", "cpp", "cross-platform", "microsoft", "cloud")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    _sdks = (
        "azure-core",
        "azure-template",
        "azure-security-keyvault-administration",
        "azure-security-keyvault-certificates",
        "azure-security-keyvault-secrets",
        "azure-security-attestation",
        "azure-security-keyvault-keys",
        "azure-data-tables",
        "azure-identity",
        "azure-storage-common",
        "azure-storage-queues",
        "azure-storage-files-shares",
        "azure-storage-blobs",
        "azure-storage-files-datalake"
    )
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("libcurl/[>=7.78 <9]")
        self.requires("libxml2/[>=2.12.5 <3]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)

        # Open to contributions for windows and apple
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                f"{self.ref} is not supported on {self.settings.os}.")

        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration(
                f"{self.ref} is not supported on {self.settings.compiler}.")

        if self.settings.compiler == 'gcc' and Version(self.settings.compiler.version) < "6":
            raise ConanInvalidConfiguration("Building requires GCC >= 6")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = "OFF"
        tc.cache_variables["BUILD_SAMPLES"] = "OFF"
        tc.cache_variables["BUILD_WINDOWS_UWP"] = "ON"
        tc.cache_variables["DISABLE_AZURE_CORE_OPENTELEMETRY"] = "ON"
        tc.cache_variables["BUILD_TRANSPORT_CURL"] = "ON"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "AzureSDK")

        for sdk in self._sdks:
            self.cpp_info.components[sdk].set_property("cmake_target_name", f"Azure::{sdk}")
            self.cpp_info.components[sdk].libs = [sdk]

            # TODO: to remove in conan v2 once cmake_find_package_* generators removed
            self.cpp_info.components[sdk].names["cmake_find_package"] = sdk
            self.cpp_info.components[sdk].names["cmake_find_package_multi"] = sdk
            self.cpp_info.components[sdk].requires.extend(["libcurl::curl", "libxml2::libxml2"])

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "AzureSDK"
        self.cpp_info.filenames["cmake_find_package_multi"] = "AzureSDK"
        self.cpp_info.names["cmake_find_package"] = "Azure"
        self.cpp_info.names["cmake_find_package_multi"] = "Azure"
        self.cpp_info.components["azure-core"].names["cmake_find_package"] = "azure-core"
        self.cpp_info.components["azure-core"].names["cmake_find_package_multi"] = "azure-core"
