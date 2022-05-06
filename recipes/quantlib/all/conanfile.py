from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.45.0"


class QuantlibConan(ConanFile):
    name = "quantlib"
    description = "QuantLib is a free/open-source library for modeling, trading, and risk management in real-life."
    license = "BSD-3-Clause"
    topics = ("quantlib", "quantitative-finance")
    homepage = "https://www.quantlib.org"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "high_resolution_date": [True, False],
        "with_openmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "high_resolution_date": False,
        "with_openmp": False,
    }

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.Version(self.version) < "1.24":
            del self.options.high_resolution_date
            del self.options.with_openmp

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.79.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("gcc < 5 not supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        if tools.Version(self.version) < "1.24":
            cmake.definitions["USE_BOOST_DYNAMIC_LIBRARIES"] = False # even if boost shared, the underlying upstream logic doesn't matter for conan
            if is_msvc(self):
                cmake.definitions["MSVC_RUNTIME"] = "static" if is_msvc_static_runtime(self) else "dynamic"
        else:
            cmake.definitions["QL_BUILD_BENCHMARK"] = False
            cmake.definitions["QL_BUILD_EXAMPLES"] = False
            cmake.definitions["QL_BUILD_TEST_SUITE"] = False
            cmake.definitions["QL_ENABLE_OPENMP"] = self.options.with_openmp
            cmake.definitions["QL_HIGH_RESOLUTION_DATE"] = self.options.high_resolution_date
            cmake.definitions["QL_INSTALL_BENCHMARK"] = False
            cmake.definitions["QL_INSTALL_EXAMPLES"] = False
            cmake.definitions["QL_INSTALL_TEST_SUITE"] = False
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.TXT", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "QuantLib")
        self.cpp_info.set_property("cmake_target_name", "QuantLib::QuantLib")
        self.cpp_info.set_property("pkg_config_name", "quantlib")
        self.cpp_info.libs = tools.collect_libs(self)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "QuantLib"
        self.cpp_info.names["cmake_find_package_multi"] = "QuantLib"
