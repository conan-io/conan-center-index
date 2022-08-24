from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


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

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
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
        self.requires("boost/1.76.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 11)
        if self.settings.compiler == "gcc" and tools.scm.Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("gcc < 5 not supported")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_BOOST_DYNAMIC_LIBRARIES"] = False # even if boost shared, the underlying upstream logic doesn't matter for conan
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["MSVC_RUNTIME"] = "dynamic" if "MD" in str(self.settings.compiler.runtime) else "static"
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.TXT", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "quantlib"
        self.cpp_info.libs = tools.files.collect_libs(self, self)
