import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


required_conan_version = ">=1.33.0"


class MsixConan(ConanFile):
    name = "msix"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/msix-packaging"
    description = "An SDK for creating MSIX packages"
    topics = ("msix", "sdk", "packaging", "conan-recipe")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "crypto_lib": ["crypt32", "openssl"],
        "pack": [True, False],
        "skip_bundles": [True, False],
        "use_external_zlib": [True, False],
        "use_validation_parser": [True, False],
        "xml_parser": ["applexml", "javaxml", "msxml6", "xerces"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "crypto_lib": "openssl",
        "pack": False,
        "skip_bundles": False,
        "use_external_zlib": True,
        "use_validation_parser": False,
        "xml_parser": "xerces"
    }

    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/**"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.settings.os == "Android":
            self._cmake.definitions["AOSP"] = True
        if self.settings.os == "Linux":
            self._cmake.definitions["LINUX"] = True
        if self.settings.os == "Macos":
            self._cmake.definitions["MACOS"] = True
        self._cmake.definitions["CRYPTO_LIB"] = self.options.crypto_lib
        self._cmake.definitions["MSIX_PACK"] = self.options.pack
        self._cmake.definitions["MSIX_SAMPLES"] = False
        self._cmake.definitions["MSIX_TESTS"] = False
        self._cmake.definitions["SKIP_BUNDLES"] = self.options.skip_bundles
        self._cmake.definitions["USE_EXTERNAL_ZLIB"] = self.options.use_external_zlib
        self._cmake.definitions["USE_SHARED_ZLIB"] = self.options["zlib"].shared
        self._cmake.definitions["USE_VALIDATION_PARSER"] = self.options.use_validation_parser
        self._cmake.definitions["XML_PARSER"] = self.options.xml_parser
        self._cmake.configure()
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Linux" and (self.settings.compiler != "clang"):
            raise ConanInvalidConfiguration("Only clang is supported on Linux")
        if self.settings.os == "Linux" and self.options.shared:
            self.options.fPIC = True
        if self.settings.os != "Android" and self.options.xml_parser == "javaxml":
            raise ConanInvalidConfiguration("javaxml is supported only for Android")
        if self.settings.os != "Macos" and self.options.xml_parser == "applexml":
            raise ConanInvalidConfiguration("applexml is supported only for MacOS")
        if self.settings.os != "Windows" and (self.options.crypto_lib == "crypt32"):
            raise ConanInvalidConfiguration("crypt32 is supported only for Windows")
        if self.settings.os != "Windows" and self.options.xml_parser == "msxml6":
            raise ConanInvalidConfiguration("msxml6 is supported only for Windows")
        if self.options.pack:
            if self.settings.os == "Macos":
                if not self.options.use_external_zlib:
                    raise ConanInvalidConfiguration("Using libCompression APIs and packaging features is not supported")
                if self.options.xml_parser and (self.options.xml_parser != "xerces"):
                    raise ConanInvalidConfiguration("Xerces is the only supported parser for MacOS pack")
            if not self.options.use_validation_parser:
                raise ConanInvalidConfiguration("Packaging requires validation parser")
        if self.options.xml_parser == "xerces":
            self.options["xerces-c"].char_type = "char16_t"
            self.options["xerces-c"].shared = False
        tools.check_min_cppstd(self, "14")

    def requirements(self):
        if self.settings.os == "Linux" and not self.options.skip_bundles:
            self.requires("icu/68.2")
        if self.options.crypto_lib == "openssl":
            self.requires("openssl/1.0.2t")
        if self.options.use_external_zlib:
            self.requires("zlib/1.2.11")
        if self.options.xml_parser == "xerces":
            self.requires("xerces-c/3.2.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["runtimeobject"]
            if self.settings.compiler == "Visual Studio":
                self.cpp_info.system_libs.append("delayimp")
            if self.options.crypto_lib == "crypt32":
                self.cpp_info.system_libs.extend(["bcrypt", "crypt32", "wintrust"])
            if self.options.xml_parser == "msxml6":
                self.cpp_info.system_libs.append("msxml6")
