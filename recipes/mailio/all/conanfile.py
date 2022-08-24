from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class mailioConan(ConanFile):
    name = "mailio"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/karastojko/mailio"
    description = "mailio is a cross platform C++ library for MIME format and SMTP, POP3 and IMAP protocols."
    topics = ("smtp", "imap", "email", "mail", "libraries", "cpp")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "shared": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False
    }
    generators = "cmake", "cmake_find_package"
    short_paths = True
    _cmake = None

    _compiler_required_cpp17 = {
        "gcc": "8.3",
        "clang": "6",
        "Visual Studio": "15",
        "apple-clang": "10",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["MAILIO_BUILD_SHARED_LIBRARY"] = self.options.shared
            self._cmake.definitions["MAILIO_BUILD_DOCUMENTATION"] = False
            self._cmake.definitions["MAILIO_BUILD_EXAMPLES"] = False
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.79.0")
        self.requires("openssl/1.1.1q")

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.build.check_min_cppstd(self, self, "17")
        try:
            minimum_required_compiler_version = self._compiler_required_cpp17[str(self.settings.compiler)]
            if tools.Version(self.settings.compiler.version) < minimum_required_compiler_version:
                raise ConanInvalidConfiguration("This package requires c++17 support. The current compiler does not support it.")
        except KeyError:
            self.output.warn("This recipe has no support for the current compiler. Please consider adding it.")

    def build_requirements(self):
        # mailio requires cmake >= 3.16.3
        self.build_requires("cmake/3.23.2")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["mailio"]
        self.cpp_info.requires = ["boost::system", "boost::date_time", "boost::regex", "openssl::openssl"]
