from conan import ConanFile
from conans import CMake, tools
from conan.tools.files import get, copy, replace_in_file
from conan.errors import ConanInvalidConfiguration
# TODO: Replace by from conan.tools.build import check_min_cppstd after 1.50
from conans.tools import check_min_cppstd, Version
import functools
import os

required_conan_version = ">=1.47.0"


class OpenTDFConan(ConanFile):
    name = "opentdf-client"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.virtru.com"
    topics = ("opentdf", "opentdf-client", "tdf", "virtru")
    description = "openTDF core c++ client library for creating and accessing TDF protected data"
    license = "BSD-3-Clause-Clear"
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"build_python": [True, False], "fPIC": [True, False]}
    default_options = {"build_python": False, "fPIC": True}

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
            "Visual Studio": "17",
            "msvc": "19.22",
            "gcc": "7.5.0",
            "clang": "12",
            "apple-clang": "12.0.0",
        }

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn(f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support.")
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(f"{self.name} requires C++{self._minimum_cpp_standard} support."
                                                 "The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it.")

    def requirements(self):
        self.requires("openssl/1.1.1q")
        self.requires("boost/1.79.0")
        self.requires("ms-gsl/2.1.0")
        self.requires("libxml2/2.9.14")
        self.requires("libarchive/3.6.1")
        self.requires("nlohmann_json/3.11.1")
        self.requires("jwt-cpp/0.4.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        copy(self, "*", dst="lib", src=os.path.join(self._source_subfolder,"tdf-lib-cpp", "lib"))
        copy(self, "*", dst="include", src=os.path.join(self._source_subfolder,"tdf-lib-cpp", "include"))
        copy(self, "LICENSE", dst="licenses", src=os.path.join(self._source_subfolder,"tdf-lib-cpp"))

    # TODO - this only advertises the static lib, add dynamic lib also
    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "opentdf-client")
        self.cpp_info.set_property("cmake_target_name", "opentdf-client::opentdf-client")
        self.cpp_info.set_property("pkg_config_name", "opentdf-client")

        self.cpp_info.components["libopentdf"].libs = ["opentdf_static"]
        self.cpp_info.components["libopentdf"].set_property("cmake_target_name", "copentdf-client::opentdf-client")
        self.cpp_info.components["libopentdf"].names["cmake_find_package"] = "opentdf-client"
        self.cpp_info.components["libopentdf"].names["cmake_find_package_multi"] = "opentdf-client"
        self.cpp_info.components["libopentdf"].names["pkg_config"] = "opentdf-client"
        self.cpp_info.components["libopentdf"].requires = ["openssl::openssl", "boost::boost", "ms-gsl::ms-gsl", "libxml2::libxml2", "libarchive::libarchive", "jwt-cpp::jwt-cpp", "nlohmann_json::nlohmann_json"]
