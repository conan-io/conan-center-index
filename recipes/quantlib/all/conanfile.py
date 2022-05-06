from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools

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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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
        cmake.definitions["USE_BOOST_DYNAMIC_LIBRARIES"] = False # even if boost shared, the underlying upstream logic doesn't matter for conan
        if is_msvc(self):
            cmake.definitions["MSVC_RUNTIME"] = "static" if is_msvc_static_runtime(self) else "dynamic"
        cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.TXT", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "quantlib")
        self.cpp_info.libs = tools.collect_libs(self)
