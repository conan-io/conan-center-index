import os
from conan import ConanFile, tools
from conan.tools.scm import Git
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout

class OpenTDFConan(ConanFile):

    name = "opentdf-client"
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.virtru.com"
    topics = ("opentdf", "opentdf-client", "tdf", "virtru")
    description = "openTDF core c++ client library for creating and accessing TDF protected data"
    license = "BSD-3-Clause-Clear"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False], "without_libiconv": [True, False], "without_zlib": [True, False], "branch_version": [True, False]}
    default_options = {"fPIC": True, "without_libiconv": True, "without_zlib": True, "branch_version": False}

    exports_sources = ["CMakeLists.txt"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 17

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def source(self):
        if self.options.branch_version:
            git = tools.Git(folder=self._source_subfolder)
            git.clone("git@github.com:opentdf/client-cpp.git", self.version)
        else:
            tools.files.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        conan.tools.files.copy(self, "*", os.path.join(self._source_subfolder,"tdf-lib-cpp/lib"), "lib")
        conan.tools.files.copy(self, "*", os.path.join(self._source_subfolder,"tdf-lib-cpp/include"), "include")
        conan.tools.files.copy(self, "LICENSE", os.path.join(self._source_subfolder,"tdf-lib-cpp"), "licenses")

    def package_info(self):
        self.cpp_info.components["libopentdf"].libs = ["opentdf_static"]
        self.cpp_info.components["libopentdf"].names["cmake_find_package"] = "opentdf-client"
        self.cpp_info.components["libopentdf"].names["cmake_find_package_multi"] = "opentdf-client"
        self.cpp_info.components["libopentdf"].names["pkg_config"] = "opentdf-client"
        self.cpp_info.components["libopentdf"].requires = ["openssl::openssl", "boost::boost", "ms-gsl::ms-gsl", "libxml2::libxml2", "jwt-cpp::jwt-cpp", "nlohmann_json::nlohmann_json"]

    def configure(self):
        if self.options.without_zlib:
            self.options["libxml2"].zlib = False
        if self.options.without_libiconv:
            self.options["boost"].without_locale = True
            self.options["boost"].without_log = True

    def requirements(self):
        self.requires("openssl/1.1.1q@")
        self.requires("boost/1.76.0@")
        self.requires("ms-gsl/2.1.0@")
        self.requires("libxml2/2.9.10@")
        self.requires("nlohmann_json/3.10.4@")
        self.requires("jwt-cpp/0.4.0@")
        # We do not require zlib but conan-center provides default build binaries, and boost+libxml2
        # specify differerent versions, which causes a build fail due to the dependency conflict.
        # Overriding the version here allows a clean build with the stock build settings.
        if not self.options.without_zlib:
            self.requires("zlib/1.2.12@")
        # Same for libiconv
        if not self.options.without_libiconv:
            self.requires("libiconv/2.17@")
