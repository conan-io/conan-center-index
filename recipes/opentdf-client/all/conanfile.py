from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
import os

required_conan_version = ">=1.40.0"


class OpenTDFConan(ConanFile):
    name = "opentdf-client"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.virtru.com"
    topics = ("opentdf", "opentdf-client", "tdf", "virtru")
    description = "openTDF core c++ client library for creating and accessing TDF protected data"
    license = "BSD-3-Clause-Clear"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"build_python": [True, False], "fPIC": [True, False], "without_libiconv": [True, False], "without_zlib": [True, False], "branch_version": [True, False]}
    default_options = {"build_python": False, "fPIC": True, "without_libiconv": False, "without_zlib": False, "branch_version": False}
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

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "7.0.0",
            "clang": "12",
            "apple-clang": "12.0.0"
        }

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def configure(self):
        if self.options.without_zlib:
            self.options["libxml2"].zlib = False
        if self.options.without_libiconv:
            self.options["boost"].without_locale = True
            self.options["boost"].without_log = True

    def requirements(self):
        self.requires("openssl/1.1.1o@")
        self.requires("boost/1.76.0@")
        self.requires("ms-gsl/2.1.0@")
        self.requires("libxml2/2.9.10@")
        self.requires("nlohmann_json/3.10.4@")
        self.requires("jwt-cpp/0.4.0@")
        # We do not require zlib but conan-center only allows 'stock' references, and boost+libxml2
        # specify differerent versions, which causes a build fail due to the dependency conflict.
        # Overriding the version here allows a clean build with the stock build settings.
        if not self.options.without_zlib:
            self.requires("zlib/1.2.12@")
        # ...and same for libiconv
        if not self.options.without_libiconv:
            self.requires("libiconv/1.17@")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        if self.options.branch_version:
            self.output.warn("Building branch_version = {}".format(self.version))
            self.run("git clone git@github.com:opentdf/client-cpp.git --depth 1 --branch " + self.version + " " + self._source_subfolder)
        else:
            tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        tc.build()

    def package(self):
        tc.install()
        self.copy("*", dst="lib", src=os.path.join(self._source_subfolder,"tdf-lib-cpp/lib"))
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder,"tdf-lib-cpp/include"))
        self.copy("LICENSE", dst="licenses", src=os.path.join(self._source_subfolder,"tdf-lib-cpp"))

    # TODO - this only advertises the static lib, add dynamic lib also
    def package_info(self):
        self.cpp_info.components["libopentdf"].libs = ["opentdf_static"]
        self.cpp_info.components["libopentdf"].names["cmake_find_package"] = "opentdf-client"
        self.cpp_info.components["libopentdf"].names["cmake_find_package_multi"] = "opentdf-client"
        self.cpp_info.components["libopentdf"].names["pkg_config"] = "opentdf-client"
        if self.options.without_zlib:
            self.cpp_info.components["libopentdf"].requires = ["openssl::openssl", "boost::boost", "ms-gsl::ms-gsl", "libxml2::libxml2", "jwt-cpp::jwt-cpp", "nlohmann_json::nlohmann_json"]
        else:
            self.cpp_info.components["libopentdf"].requires = ["openssl::openssl", "boost::boost", "ms-gsl::ms-gsl", "libxml2::libxml2", "jwt-cpp::jwt-cpp", "nlohmann_json::nlohmann_json", "zlib::zlib"]
