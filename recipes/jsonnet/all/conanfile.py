from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class JsonnetConan(ConanFile):
    name = "jsonnet"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/jsonnet"
    description = "Jsonnet - The data templating language"
    topics = ("config", "json", "functional", "configuration")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("nlohmann_json/3.9.1")

    def validate(self):
        if hasattr(self, "settings_build") and tools.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("jsonnet does not support cross building")

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        self._cmake.definitions["BUILD_JSONNET"] = False
        self._cmake.definitions["BUILD_JSONNETFMT"] = False
        self._cmake.definitions["USE_SYSTEM_JSON"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.components["libjsonnet"].libs = ["jsonnet"]
        self.cpp_info.components["libjsonnet"].requires = ["nlohmann_json::nlohmann_json"]
        if tools.stdcpp_library(self):
            self.cpp_info.components["libjsonnet"].system_libs.append(tools.stdcpp_library(self))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libjsonnet"].system_libs.append("m")

        self.cpp_info.components["libjsonnetpp"].libs = ["jsonnet++"]
        self.cpp_info.components["libjsonnetpp"].requires = ["libjsonnet"]
