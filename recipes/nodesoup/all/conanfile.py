from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class NodesoupConan(ConanFile):
    name = "nodesoup"
    description = "Force-directed graph layout with Fruchterman-Reingold"
    license = "MIT",
    topics = ("graph", "visualization", "layout", "kamada", "kawai", "fruchterman", "reingold")
    homepage = "https://github.com/olvb/nodesoup"
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

    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/*"

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

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 14)
        if self.settings.compiler == "clang":
            if tools.Version(self.settings.compiler.version) < "5.0" and self.settings.compiler.libcxx in ("libstdc++", "libstdc++11"):
                raise ConanInvalidConfiguration("The version of libstdc++(11) of the current compiler does not support building nodesoup")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "nodesoup"))
        self.cpp_info.libs = ["nodesoup"]
        self.cpp_info.names["cmake_find_package"] = "nodesoup"
        self.cpp_info.names["cmake_find_package_multi"] = "nodesoup"
