import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class AzureStorageCppConan(ConanFile):
    name = "azure-storage-cpp"
    description = "Microsoft Azure Storage Client Library for C++"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Azure/azure-storage-cpp"
    topics = ("azure", "cpp", "cross-platform", "microsoft", "cloud")

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
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _minimum_compiler_version(self):
        return {
            "gcc": "6",
            "Visual Studio": "14",
            "msvc": "190",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
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
        self.requires("cpprestsdk/2.10.19", transitive_headers=True, transitive_libs=True)
        self.requires("libxml2/[>=2.12.5 <3]", transitive_headers=True, transitive_libs=True)
        if self.settings.os != "Windows":
            # Boost.Asio is used in a public header here:
            # https://github.com/Azure/azure-storage-cpp/blob/v7.5.0/Microsoft.WindowsAzure.Storage/includes/wascore/timer_handler.h#L27
            self.requires("boost/1.83.0", transitive_headers=True, transitive_libs=True)
            self.requires("util-linux-libuuid/2.39.2", transitive_headers=True, transitive_libs=True)
            self.requires("openssl/[>=1.1 <4]")
        if is_apple_os(self):
            self.requires("libgettext/0.22")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compiler_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warning(
                f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support."
            )
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires C++{self._minimum_cpp_standard} support. The current compiler"
                    f" {self.settings.compiler} {self.settings.compiler.version} does not support it."
                )

        # FIXME: Visual Studio 2015 & 2017 are supported but CI of CCI lacks several Win SDK components
        # https://github.com/conan-io/conan-center-index/issues/4195
        if not check_min_vs(self, 192, raise_invalid=False):
            raise ConanInvalidConfiguration("Visual Studio < 2019 not yet supported in this recipe")
        if self.options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio build for shared library with MT runtime is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_FIND_FRAMEWORK"] = "LAST"
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_SAMPLES"] = False
        if is_apple_os(self):
            tc.variables["GETTEXT_LIB_DIR"] = self.dependencies["libgettext"].cpp_info.libdir
        if not valid_min_cppstd(self, self._minimum_cpp_standard):
            tc.variables["CMAKE_CXX_STANDARD"] = self._minimum_cpp_standard
        # Allow non-cache_variables to be used
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        # Relocatable shared libs on macOS
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("util-linux-libuuid", "cmake_file_name", "UUID")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        cmakelists_path = os.path.join(self.source_folder, "Microsoft.WindowsAzure.Storage", "CMakeLists.txt")
        # Do not force C++11 and libc++
        replace_in_file(self, cmakelists_path, "-std=c++11", "")
        replace_in_file(self, cmakelists_path, "-stdlib=libc++", "")
        # Let Conan handle the Boost defines
        replace_in_file(self, cmakelists_path, "add_definitions(-DBOOST_LOG_DYN_LINK)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        if self.settings.os == "Windows":
            # https://github.com/Azure/azure-storage-cpp/blob/v7.5.0/Microsoft.WindowsAzure.Storage/src/CMakeLists.txt#L100
            self.cpp_info.libs = ["wastorage"]
            # https://github.com/Azure/azure-storage-cpp/blob/v7.5.0/Microsoft.WindowsAzure.Storage/src/CMakeLists.txt#L90
            self.cpp_info.system_libs = ["ws2_32", "rpcrt4", "xmllite", "bcrypt"]
            if is_msvc(self):
                # https://github.com/Azure/azure-storage-cpp/blob/v7.5.0/Microsoft.WindowsAzure.Storage/CMakeLists.txt#L116-L120
                if self.options.shared:
                    self.cpp_info.defines = ["WASTORAGE_DLL", "_USRDLL"]
                else:
                    self.cpp_info.defines = ["_NO_WASTORAGE_API"]
        else:
            self.cpp_info.libs = ["azurestorage"]
