from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rmdir, apply_conandata_patches, export_conandata_patches
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

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "transport_winhttp": [True, False],
        "transport_curl": [True, False]
    }

    default_options = {"shared": False, "fPIC": True}

    default_options = {
        "shared": False,
        "fPIC": True,
        "transport_winhttp": True,
        "transport_curl": True
    }

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.transport_winhttp

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")
        self.requires("libxml2/[>=2.12.5 <3]")

        if self.settings.os == "Windows":
            # wil is always required on windows since azure-identity can't be disabled via cmake.
            # azure-identity and wil are not necessary for storage if skip_test=True, but MS
            # doesn't currently support that build option...
            self.requires("wil/1.0.250325.1")

        if self.options.transport_curl:
            self.requires("libcurl/[>=7.78 <9]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)

        if self.settings.os == "Windows":
            if not self.options.transport_curl and not self.options.get_safe("transport_winhttp"):
                raise ConanInvalidConfiguration("On Windows, HTTP Transport options: transport_winhttp or transport_curl must be enabled.")
        elif not self.options.transport_curl:
                raise ConanInvalidConfiguration("The HTTP Transport option transport_curl must be enabled.")

        if self.settings.compiler == 'gcc' and Version(self.settings.compiler.version) < "6":
            raise ConanInvalidConfiguration("Building requires GCC >= 6")

        if (self.settings.compiler == 'clang' or self.settings.compiler == "apple-clang") and Version(self.settings.compiler.version) < "10":
            raise ConanInvalidConfiguration("Building requires Clang >= 10")

    def generate(self):
        tc = CMakeToolchain(self)

        tc.cache_variables["BUILD_TESTING"] = "OFF"
        tc.cache_variables["ENABLE_PROXY_TESTS"] = "OFF"

        tc.cache_variables["BUILD_TRANSPORT_CURL"] = self.options.transport_curl

        if self.settings.os == "Windows":
            # if transport_curl and transport_winhttp are both enabled, the SDK uses win_http by default
            # when the transport is not manually overridden when the classes are instantiated
            tc.cache_variables["BUILD_TRANSPORT_WINHTTP"] = self.options.get_safe("transport_winhttp")

        tc.cache_variables["BUILD_DOCUMENTATION"] = "OFF"
        tc.cache_variables["BUILD_SAMPLES"] = "OFF"
        tc.cache_variables["BUILD_PERFORMANCE_TESTS"] = "OFF"

        tc.cache_variables["FETCH_SOURCE_DEPS"] = "OFF"

        tc.cache_variables["WARNINGS_AS_ERRORS"] = "OFF"

        tc.cache_variables["DISABLE_AZURE_CORE_OPENTELEMETRY"] = "ON"

        tc.cache_variables["DISABLE_AMQP"] = "ON"

        tc.cache_variables["DISABLE_RUST_IN_BUILD"] = "ON"

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

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

        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "AzureSDK")

        # core component
        self.cpp_info.components["azure-core"].set_property("cmake_target_name", "Azure::azure-core")
        self.cpp_info.components["azure-core"].libs = ["azure-core"]

        self.cpp_info.components["azure-core"].requires.extend(["openssl::openssl", "libxml2::libxml2"])

        if self.settings.os == "Windows" and self.options.get_safe("transport_winhttp"):
            self.cpp_info.components["azure-core"].requires.append("wil::wil")
            self.cpp_info.components["azure-core"].system_libs = ["winhttp"]
        if self.options.transport_curl:
            self.cpp_info.components["azure-core"].requires.append("libcurl::libcurl")

        self.cpp_info.components["azure-storage-common"].set_property("cmake_target_name", "Azure::azure-storage-common")
        self.cpp_info.components["azure-storage-common"].libs = ["azure-storage-common"]
        self.cpp_info.components["azure-storage-common"].requires = ["azure-core"]
        if not self.settings.os == "Windows":
            self.cpp_info.components["azure-storage-common"].requires.extend(["openssl::openssl", "libxml2::libxml2"])

        self.cpp_info.components["azure-storage-blobs"].set_property("cmake_target_name", "Azure::azure-storage-blobs")
        self.cpp_info.components["azure-storage-blobs"].libs = ["azure-storage-blobs"]
        self.cpp_info.components["azure-storage-blobs"].requires = ["azure-core", "azure-storage-common"]

        self.cpp_info.components["azure-storage-files-shares"].set_property("cmake_target_name", "Azure::azure-storage-files-shares")
        self.cpp_info.components["azure-storage-files-shares"].libs = ["azure-storage-files-shares"]
        self.cpp_info.components["azure-storage-files-shares"].requires = ["azure-core", "azure-storage-common"]

        self.cpp_info.components["azure-identity"].set_property("cmake_target_name", "Azure::azure-identity")
        self.cpp_info.components["azure-identity"].libs = ["azure-identity"]
        self.cpp_info.components["azure-identity"].requires = ["azure-core"]
        if self.settings.os == "Windows":
            self.cpp_info.components["azure-identity"].system_requires = ["bcrypt", "crypt32"]
        else:
            self.cpp_info.components["azure-identity"].requires.append("openssl::openssl")

        self.cpp_info.components["azure-storage-files-datalake"].set_property("cmake_target_name", "Azure::azure-storage-files-datalake")
        self.cpp_info.components["azure-storage-files-datalake"].libs = ["azure-storage-files-datalake"]
        self.cpp_info.components["azure-storage-files-datalake"].requires = ["azure-core", "azure-storage-common", "azure-storage-blobs"]

        if self.settings.os == "Windows":
            self.cpp_info.components["azure-identity"].requires.append("wil::wil")
