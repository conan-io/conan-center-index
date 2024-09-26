import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rmdir

required_conan_version = ">=1.54.0"


class AzureSDKForCppConan(ConanFile):
    name = "azure-sdk-for-cpp"
    description = "Azure SDK for C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Azure/azure-sdk-for-cpp"
    topics = ("azure", "cpp", "cross-platform", "microsoft", "cloud")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_rtti": [True, False],
        "build_transport_curl": [True, False],
        "build_transport_winhttp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_rtti": True,
        "build_transport_curl": True,
        "build_transport_winhttp": False,
    }

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os in ["Windows", "WindowsStore"]:
            del self.options.fPIC
        else:
            del self.options.build_transport_winhttp

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")
        if self.settings.os in ["Windows", "WindowsStore"]:
            self.requires("wil/1.0.240803.1")
        else:
            self.requires("libxml2/[>=2.12.5 <3]")
        if self.options.build_transport_curl:
            self.requires("libcurl/[>=7.78 <9]")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)
        if not self.options.build_transport_curl and not self.options.get_safe("build_transport_winhttp"):
            raise ConanInvalidConfiguration("At least one of 'build_transport_curl' or 'build_transport_winhttp' must be enabled")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_RTTI"] = self.options.build_rtti
        tc.cache_variables["AZ_ALL_LIBRARIES"] = True
        tc.cache_variables["FETCH_SOURCE_DEPS"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BUILD_WINDOWS_UWP"] = True
        tc.cache_variables["DISABLE_AZURE_CORE_OPENTELEMETRY"] = True
        tc.cache_variables["BUILD_TRANSPORT_CURL"] = self.options.build_transport_curl
        tc.cache_variables["BUILD_TRANSPORT_WINHTTP"] = self.options.get_safe("build_transport_winhttp", False)
        tc.cache_variables["WARNINGS_AS_ERRORS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        # This find_package() name is unofficial
        self.cpp_info.set_property("cmake_file_name", "AzureSDK")

        def _add_component(name, requires=None):
            component = self.cpp_info.components[name]
            # TODO: each component should export a separate .cmake config file,
            #  but it's not supported by Conan yet
            # component.set_property("cmake_file_name", f"{name}-cpp")
            component.set_property("cmake_target_name", f"Azure::{name}")
            component.libs = [name]
            if name != "azure-core":
                component.requires = ["azure-core"]
            component.requires.extend(requires or [])
            if self.options.build_rtti:
                component.defines.append("AZ_RTTI")
            return component

        # https://github.com/Azure/azure-sdk-for-cpp/blob/azure-core_1.13.0/sdk/core/azure-core/CMakeLists.txt#L170-L188
        core = _add_component("azure-core")
        if self.settings.os in ["Linux", "FreeBSD"]:
            core.system_libs = ["pthread"]
        if self.settings.os in ["Windows", "WindowsStore"]:
            if self.options.build_transport_curl:
                core.system_libs.append("ws2_32")
            if self.options.build_transport_winhttp:
                core.requires.append("wil::wil")
                core.system_libs.append("winhttp")
        if self.options.build_transport_curl:
            core.requires.append("libcurl::curl")
        # Add all crypto libs here, skip them for components
        if self.settings.os in ["Windows", "WindowsStore"]:
            core.system_libs = ["bcrypt", "crypt32"]
        else:
            core.requires.append("openssl::openssl")

        # https://github.com/Azure/azure-sdk-for-cpp/blob/azure-core_1.13.0/sdk/storage/azure-storage-common/CMakeLists.txt#L98-L106
        storage_common = _add_component("azure-storage-common")
        if self.settings.os in ["Windows", "WindowsStore"]:
            storage_common.system_libs.append("webservices")
        else:
            storage_common.requires.append("libxml2::libxml2")

        # https://github.com/Azure/azure-sdk-for-cpp/blob/azure-core_1.13.0/sdk/tables/azure-data-tables/CMakeLists.txt#L85-L94
        data_tables = _add_component("azure-data-tables")
        if self.settings.os in ["Windows", "WindowsStore"]:
            data_tables.system_libs.append("webservices")
        else:
            data_tables.requires.append("libxml2::libxml2")

        # https://github.com/Azure/azure-sdk-for-cpp/blob/azure-core_1.13.0/sdk/identity/azure-identity/CMakeLists.txt#L106-L112
        identity = _add_component("azure-identity")
        if self.settings.os in ["Windows", "WindowsStore"]:
            identity.requires.append("wil::wil")

        _add_component("azure-security-attestation", requires=["openssl::crypto"])
        _add_component("azure-security-keyvault-administration")
        _add_component("azure-security-keyvault-certificates")
        _add_component("azure-security-keyvault-keys")
        _add_component("azure-security-keyvault-secrets")
        _add_component("azure-storage-blobs", requires=["azure-storage-common"])
        _add_component("azure-storage-files-datalake", requires=["azure-storage-blobs", "azure-storage-common"])
        _add_component("azure-storage-files-shares", requires=["azure-storage-common"])
        _add_component("azure-storage-queues", requires=["azure-storage-common"])
        _add_component("azure-template")
