from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class ForestDBConan(ConanFile):
    name = "forestdb"
    description = "ForestDB is a KeyValue store based on a Hierarchical B+-Tree."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ForestDB-KVStore/forestdb"
    topics = ("forestdb", "kv store")
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_snappy": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_snappy": False,
    }

    generators = "cmake"

    exports_sources = ["CMakeLists.txt"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.Git(folder=self._source_subfolder).clone(**self.conan_data["sources"][self.version], shallow=True)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["SNAPPY_OPTION"] = "Disable"
        if self.options.with_snappy:
            cmake.definitions["SNAPPY_OPTION"] = "Enable"
        cmake.configure()
        cmake.build()

    def package(self):
        if not self.options.shared:
            self.copy("*.a*", dst="lib", src="lib", symlinks=True)
            self.copy("*.lib", dst="lib", src="lib", symlinks=True)
        else:
            self.copy("*.so*", dst="lib", src="lib", symlinks=True)
            self.copy("*.dylib*", dst="lib", src="lib", symlinks=True)
            self.copy("*.dll*", dst="lib", src="lib")
        self.copy("*.h", dst="include/", src="{}/include".format(self._source_subfolder), keep_path=True)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread", "dl"])
