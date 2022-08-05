from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conans import CMake, tools
from conan.tools.files import get, copy, patch
# TODO: Replace by from conan.tools.build import check_min_cppstd after 1.50
from conans.tools import check_min_cppstd
from conan.tools.scm import Version
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
    options = {"with_libiconv": [True, False], "with_zlib": [True, False], "with_libarchive": [True, False], "fPIC": [True, False], "branch_version": [True, False]}
    # opentdf-client does not need libiconv or zlib, they are required by default by boost and libxml,
    # because of the default configuration on those packages.  The build at conan-center only allows
    # prebuilt (default) packages, so they are on by default to satisfy that situation.
    # Recommendation: disable both if you are doing a local build
    default_options = {"with_libiconv": True, "with_zlib": True, "with_libarchive": True, "fPIC": True, "branch_version": False}

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
        for data in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(data["patch_file"])

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
        self.requires("nlohmann_json/3.11.1")
        self.requires("jwt-cpp/0.4.0")
        if self.options.get_safe("with_libarchive"):
            self.requires("libarchive/3.6.1")

    def config_options(self):
        # Do not need libarchive after 1.0.0
        if Version(self.version) > "1.0.0":
            del self.options.libarchive
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self.options.with_zlib:
            self.options["libxml2"].zlib = False
        if not self.options.with_libiconv:
            self.options["boost"].without_locale = True
            self.options["boost"].without_log = True

    def source(self):
        # If branch_version is set to True, the supplied version will be treated as a branch name for git clone
        if self.options.get_safe("branch_version"):
            self.output.warn("Building branch_version = {}".format(self.version))
            self.run("git clone git@github.com:opentdf/client-cpp.git --depth 1 --branch " + self.version + " " + self._source_subfolder)
        else:
            get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for data in self.conan_data.get("patches", {}).get(self.version, []):
            patch(self, **data)

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
        copy(self, "*", dst=os.path.join(self.package_folder, "lib"), src=os.path.join(os.path.join(self._source_subfolder,"tdf-lib-cpp"), "lib"), keep_path=False)
        copy(self, "*", dst=os.path.join(self.package_folder, "include"), src=os.path.join(os.path.join(self._source_subfolder,"tdf-lib-cpp"), "include"), keep_path=False)
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self._source_subfolder, ignore_case=True, keep_path=False)

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
        self.cpp_info.components["libopentdf"].requires = ["openssl::openssl", "boost::boost", "ms-gsl::ms-gsl", "libxml2::libxml2", "jwt-cpp::jwt-cpp", "nlohmann_json::nlohmann_json"]
        if self.options.get_safe("with_libarchive"):
            self.cpp_info.components["libopentdf"].requires.append("libarchive::libarchive")
