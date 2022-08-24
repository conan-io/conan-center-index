import functools
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc, msvc_runtime_flag

required_conan_version = ">=1.33.0"


class JsonnetConan(ConanFile):
    name = "jsonnet"
    description = "Jsonnet - The data templating language"
    topics = ("config", "json", "functional", "configuration")
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/jsonnet"
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

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
            # This is a workround.
            # If jsonnet is shared, rapidyaml must be built as shared,
            # or the c4core functions that rapidyaml depends on will not be able to be found.
            # This seems to be a issue of rapidyaml.
            # https://github.com/conan-io/conan-center-index/pull/9786#discussion_r829887879
            if tools.Version(self.version) >= "0.18.0":
                self.options["rapidyaml"].shared = True

    def requirements(self):
        self.requires("nlohmann_json/3.10.5")
        if tools.Version(self.version) >= "0.18.0":
            self.requires("rapidyaml/0.4.1")

    def validate(self):
        if hasattr(self, "settings_build") and tools.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("jsonnet does not support cross building")

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

        if self.options.shared and is_msvc(self) and "d" in msvc_runtime_flag(self):
            raise ConanInvalidConfiguration("shared {} is not supported with MTd/MDd runtime".format(self.name))

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        cmake.definitions["BUILD_SHARED_BINARIES"] = False
        cmake.definitions["BUILD_JSONNET"] = False
        cmake.definitions["BUILD_JSONNETFMT"] = False
        cmake.definitions["USE_SYSTEM_JSON"] = True
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

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
        if tools.Version(self.version) >= "0.18.0":
            self.cpp_info.components["libjsonnet"].requires.append("rapidyaml::rapidyaml")

        if tools.stdcpp_library(self):
            self.cpp_info.components["libjsonnet"].system_libs.append(tools.stdcpp_library(self))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libjsonnet"].system_libs.append("m")

        self.cpp_info.components["libjsonnetpp"].libs = ["jsonnet++"]
        self.cpp_info.components["libjsonnetpp"].requires = ["libjsonnet"]
