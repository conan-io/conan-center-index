import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class MsixConan(ConanFile):
    name = "msix"
    description = "An SDK for creating MSIX packages"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/msix-packaging"
    topics = ("sdk", "packaging", "conan-recipe")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "crypto_lib": ["crypt32", "openssl"],
        "pack": [True, False],
        "skip_bundles": [True, False],
        "use_external_zlib": [True, False],
        "use_validation_parser": [True, False],
        "with_xerces": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "crypto_lib": "openssl",
        "pack": False,
        "skip_bundles": False,
        "use_external_zlib": True,
        "use_validation_parser": False,
        "with_xerces": False,
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Windows":
            del self.options.crypto_lib
        if not is_apple_os(self) and self.settings.os not in ["Windows", "Android"]:
            # with_xerces is required
            del self.options.with_xerces

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ["Linux", "FreeBSD"] and not self.options.skip_bundles:
            self.requires("icu/74.2")
        if self.options.get_safe("crypto_lib", "openssl") == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        if self.options.use_external_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.get_safe("with_xerces", True):
            self.requires("xerces-c/3.2.5")

    def _validate_compiler_settings(self):
        compiler = self.settings.compiler
        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def validate(self):
        if self.settings.os in ["Linux", "FreeBSD"] and self.settings.compiler != "clang":
            raise ConanInvalidConfiguration(f"Only clang is supported on {self.settings.os}")
        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) >= "12" and self.version == "1.7":
            # AppxPackaging.hpp:706:5: error: templates must have C++ linkage
            raise ConanInvalidConfiguration("Clang 12 and newer are not supported")
        if self.options.pack:
            if is_apple_os(self):
                if not self.options.use_external_zlib:
                    raise ConanInvalidConfiguration("Using libCompression APIs and packaging features is not supported")
                if not self.options.get_safe("with_xerces", True):
                    raise ConanInvalidConfiguration("Xerces is the only supported parser for MacOS pack")
            if not self.options.use_validation_parser:
                raise ConanInvalidConfiguration("Packaging requires validation parser")
        if self.options.get_safe("with_xerces", True) and self.dependencies["xerces-c"].options.char_type != "char16_t":
            raise ConanInvalidConfiguration("Only char16_t is supported for xerces-c")

        self._validate_compiler_settings()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os == "Android":
            tc.variables["AOSP"] = True
        if self.settings.os in ["Linux", "FreeBSD"]:
            tc.variables["LINUX"] = True
        if is_apple_os(self):
            tc.variables["MACOS"] = True
        tc.variables["CRYPTO_LIB"] = self.options.get_safe("crypto_lib", "openssl")
        tc.variables["MSIX_PACK"] = self.options.pack
        tc.variables["MSIX_SAMPLES"] = False
        tc.variables["MSIX_TESTS"] = False
        tc.variables["SKIP_BUNDLES"] = self.options.skip_bundles
        tc.variables["USE_MSIX_SDK_ZLIB"] = self.options.use_external_zlib
        tc.variables["USE_VALIDATION_PARSER"] = self.options.use_validation_parser
        if self.options.get_safe("with_xerces", True):
            tc.variables["XML_PARSER"] = "xerces"
        elif self.settings.os == "Android":
            tc.variables["XML_PARSER"] = "javaxml"
        elif is_apple_os(self):
            tc.variables["XML_PARSER"] = "applexml"
        elif self.settings.os == "Windows":
            tc.variables["XML_PARSER"] = "msxml6"
        tc.variables["CALCULATE_VERSION"] = False
        tc.variables["ENABLE_NUGET_PACKAGING"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os == "Windows":
            # https://github.com/microsoft/msix-packaging/blob/v1.7/src/msix/CMakeLists.txt#L271
            self.cpp_info.system_libs.extend(["bcrypt", "crypt32", "wintrust", "runtimeobject", "delayimp"])
            if not self.options.with_xerces:
                self.cpp_info.system_libs.append("msxml6")
        if is_apple_os(self):
            # https://github.com/microsoft/msix-packaging/blob/v1.7/src/msix/CMakeLists.txt#L364
            self.cpp_info.frameworks.extend(["CoreFoundation", "Foundation"])
            if not self.options.use_external_zlib:
                # https://github.com/microsoft/msix-packaging/blob/v1.7/src/msix/CMakeLists.txt#L285
                self.cpp_info.frameworks.append("Compression")
