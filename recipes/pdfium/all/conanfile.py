from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PdfiumConan(ConanFile):
    name = "pdfium"
    description = "PDF generation and rendering library."
    license = "BSD-3-Clause"
    topics = ("conan", "pdfium", "generate", "generation", "rendering", "pdf", "document", "print")
    homepage = "https://opensource.google/projects/pdfium"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libjpeg": "libjpeg",
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package", "pkg_config"
    short_paths = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("freetype/2.10.4")
        self.requires("icu/69.1")
        self.requires("lcms/2.11")
        self.requires("openjpeg/2.4.0")
        if self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9d")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.0")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, 14)
        minimum_compiler_versions = {
            "gcc": 8,
            "Visual Studio": 15,
        }
        min_compiler_version = minimum_compiler_versions.get(str(self.settings.compiler))
        if min_compiler_version:
            if tools.Version(self.settings.compiler.version) < min_compiler_version:
                raise ConanInvalidConfiguration("pdfium needs at least compiler version {}".format(min_compiler_version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version]["pdfium-cmake"],
                  destination="pdfium-cmake", strip_root=True)
        tools.files.get(self, **self.conan_data["sources"][self.version]["pdfium"],
                  destination=self._source_subfolder)
        tools.files.get(self, **self.conan_data["sources"][self.version]["trace_event"],
                  destination=os.path.join(self._source_subfolder, "base", "trace_event", "common"))
        tools.files.get(self, **self.conan_data["sources"][self.version]["chromium_build"],
                  destination=os.path.join(self._source_subfolder, "build"))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PDFIUM_ROOT"] = os.path.join(self.source_folder, self._source_subfolder).replace("\\", "/")
        self._cmake.definitions["PDF_LIBJPEG_TURBO"] = self.options.with_libjpeg == "libjpeg-turbo"
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["pdfium"]
        if tools.is_apple_os(self, self.settings.os):
            self.cpp_info.frameworks.extend(["Appkit", "CoreFoundation", "CoreGraphics"])

        stdcpp_library = tools.stdcpp_library(self)
        if stdcpp_library:
            self.cpp_info.system_libs.append(stdcpp_library)
