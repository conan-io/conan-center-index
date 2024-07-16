from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"

AZURE_SDK_MODULES = (
    "azure-storage-common",
    "azure-storage-blobs",
    "azure-storage-files-shares"
)

class AzureSDKForCppConan(ConanFile):
    name = "azure-sdk-for-cpp"
    description = "Microsoft Azure Storage Client Library for C++"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Azure/azure-sdk-for-cpp"
    topics = ("azure", "cpp", "cross-platform", "microsoft", "cloud")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    options.update({_name: [True, False] for _name in AZURE_SDK_MODULES})
    default_options = {"shared": False, "fPIC": True}
    default_options.update({_name: True for _name in AZURE_SDK_MODULES}) # Build all modules by default, let users pick what they do not want

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")
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
                f"{self.ref} Conan recipe in ConanCenter still does not support {self.settings.os}, contributions to the recipe welcome.")

        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration(
                f"{self.ref} Conan recipe in ConanCenter still does not support {self.settings.compiler}, contributions to the recipe welcome.")

        if self.settings.compiler == 'gcc' and Version(self.settings.compiler.version) < "6":
            raise ConanInvalidConfiguration("Building requires GCC >= 6")

    def generate(self):
        tc = CMakeToolchain(self)

        build_list = ["azure-core"]
        for sdk in AZURE_SDK_MODULES:
            if self.options.get_safe(sdk):
                build_list.append(sdk)
        tc.cache_variables["BUILD_LIST"] = ";".join(build_list)

        tc.variables["AZ_ALL_LIBRARIES"] = "ON"
        tc.variables["FETCH_SOURCE_DEPS"] = "OFF"
        tc.cache_variables["BUILD_TESTING"] = "OFF"
        tc.cache_variables["BUILD_WINDOWS_UWP"] = "ON"
        tc.cache_variables["DISABLE_AZURE_CORE_OPENTELEMETRY"] = "ON"
        tc.cache_variables["BUILD_TRANSPORT_CURL"] = "ON"
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
        self.cpp_info.components["azure-core"].requires.extend(["openssl::openssl", "libcurl::curl", "libxml2::libxml2"])

        enabled_sdks = [sdk for sdk in AZURE_SDK_MODULES if self.options.get_safe(sdk)]
        for sdk in enabled_sdks:
            self.cpp_info.components[sdk].set_property("cmake_target_name", f"Azure::{sdk}")
            self.cpp_info.components[sdk].libs = [sdk]
