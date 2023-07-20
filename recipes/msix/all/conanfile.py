import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc
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
        "xml_parser": ["auto", "applexml", "javaxml", "msxml6", "xerces"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "crypto_lib": "openssl",
        "pack": False,
        "skip_bundles": False,
        "use_external_zlib": True,
        "use_validation_parser": False,
        "xml_parser": "auto",
    }

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.crypto_lib = "crypt32"

        if self.options.xml_parser == "auto":
            if self.settings.os == "Android":
                self.options.xml_parser = "javaxml"
            elif is_apple_os(self):
                self.options.xml_parser = "applexml"
            elif self.settings.os == "Windows":
                self.options.xml_parser = "msxml6"
            else:
                self.options.xml_parser = "xerces"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        if self.options.xml_parser == "xerces":
            self.options["xerces-c"].char_type = "char16_t"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os == "Linux" and not self.options.skip_bundles:
            self.requires("icu/73.2")
        if self.options.crypto_lib == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        if self.options.use_external_zlib:
            self.requires("zlib/1.2.13")
        if self.options.xml_parser == "xerces":
            self.requires("xerces-c/3.2.4")

    def _validate_compiler_settings(self):
        compiler = self.settings.compiler
        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, "17")

        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warning(
                f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support."
            )
        elif Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(
                f"{self.name} requires C++17 support. The current compiler"
                f" {self.settings.compiler} {self.settings.compiler.version} does not support it."
            )

    def validate(self):
        if self.settings.os == "Linux" and self.settings.compiler != "clang":
            raise ConanInvalidConfiguration("Only clang is supported on Linux")
        if self.settings.os != "Android" and self.options.xml_parser == "javaxml":
            raise ConanInvalidConfiguration("javaxml is supported only for Android")
        if self.settings.os != "Macos" and self.options.xml_parser == "applexml":
            raise ConanInvalidConfiguration("applexml is supported only for MacOS")
        if self.settings.os != "Windows" and self.options.xml_parser == "msxml6":
            raise ConanInvalidConfiguration("msxml6 is supported only for Windows")
        if self.settings.os != "Windows" and self.options.crypto_lib == "crypt32":
            raise ConanInvalidConfiguration("crypt32 is supported only for Windows")
        if self.options.pack:
            if self.settings.os == "Macos":
                if not self.options.use_external_zlib:
                    raise ConanInvalidConfiguration(
                        "Using libCompression APIs and packaging features is not supported"
                    )
                if self.options.xml_parser != "xerces":
                    raise ConanInvalidConfiguration("Xerces is the only supported parser for MacOS pack")
            if not self.options.use_validation_parser:
                raise ConanInvalidConfiguration("Packaging requires validation parser")
        if self.options.xml_parser == "xerces" and self.dependencies["xerces-c"].options.char_type != "char16_t":
            raise ConanInvalidConfiguration("Only char16_t is supported for xerces-c")

        self._validate_compiler_settings()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os == "Android":
            tc.variables["AOSP"] = True
        if self.settings.os == "Linux":
            tc.variables["LINUX"] = True
        if self.settings.os == "Macos":
            tc.variables["MACOS"] = True
        tc.variables["CRYPTO_LIB"] = self.options.crypto_lib
        tc.variables["MSIX_PACK"] = self.options.pack
        tc.variables["MSIX_SAMPLES"] = False
        tc.variables["MSIX_TESTS"] = False
        tc.variables["SKIP_BUNDLES"] = self.options.skip_bundles
        tc.variables["USE_MSIX_SDK_ZLIB"] = self.options.use_external_zlib
        tc.variables["USE_SHARED_ZLIB"] = self.dependencies["zlib"].options.shared
        tc.variables["USE_VALIDATION_PARSER"] = self.options.use_validation_parser
        tc.variables["XML_PARSER"] = self.options.xml_parser
        tc.variables["CALCULATE_VERSION"] = False
        tc.variables["ENABLE_NUGET_PACKAGING"] = False
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
            self.cpp_info.system_libs = ["runtimeobject"]
            if is_msvc(self):
                self.cpp_info.system_libs.append("delayimp")
            if self.options.crypto_lib == "crypt32":
                self.cpp_info.system_libs.extend(["bcrypt", "crypt32", "wintrust"])
            if self.options.xml_parser == "msxml6":
                self.cpp_info.system_libs.append("msxml6")
