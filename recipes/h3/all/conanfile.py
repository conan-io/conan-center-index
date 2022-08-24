from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.33.0"


class H3Conan(ConanFile):
    name = "h3"
    description = "Hexagonal hierarchical geospatial indexing system."
    license = "Apache-2.0"
    topics = ("h3", "hierarchical", "geospatial", "indexing")
    homepage = "https://github.com/uber/h3"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_filters": [True, False],
        "h3_prefix": "ANY",
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_filters": True,
        "h3_prefix": "",
    }

    generators = "cmake"
    _cmake = None

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["H3_PREFIX"] = self.options.h3_prefix
        self._cmake.definitions["ENABLE_COVERAGE"] = False
        self._cmake.definitions["BUILD_BENCHMARKS"] = False
        self._cmake.definitions["BUILD_FILTERS"] = self.options.build_filters
        self._cmake.definitions["BUILD_GENERATORS"] = False
        self._cmake.definitions["WARNINGS_AS_ERRORS"] = False
        self._cmake.definitions["ENABLE_LINTING"] = False
        self._cmake.definitions["ENABLE_DOCS"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "h3"
        self.cpp_info.names["cmake_find_package_multi"] = "h3"
        self.cpp_info.libs = ["h3"]
        self.cpp_info.defines.append("H3_PREFIX={}".format(self.options.h3_prefix))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        if self.options.build_filters:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
