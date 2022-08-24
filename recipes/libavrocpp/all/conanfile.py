import os
import functools

from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.33.0"

class LibavrocppConan(ConanFile):
    name = "libavrocpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Avro is a data serialization system."
    homepage = "https://avro.apache.org/"
    topics = ("serialization", "deserialization")
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False, 
        "fPIC": True
    }
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, "11")

    def requirements(self):
        self.requires("boost/1.78.0")
        self.requires("snappy/1.1.9")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        tools.files.replace_in_file(self, 
            os.path.join(os.path.join(self._source_subfolder, "lang", "c++"), "CMakeLists.txt"),
            "${SNAPPY_LIBRARIES}", "${Snappy_LIBRARIES}"
        )

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SNAPPY_ROOT_DIR"] = self.deps_cpp_info["snappy"].rootpath.replace("\\", "/")
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("NOTICE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        if self.settings.os == "Windows":
            for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
                tools.files.rm(self, dll_pattern_to_remove, self.package_folder)

    def package_info(self):
        # FIXME: avro does not install under a CMake namespace https://github.com/apache/avro/blob/351f589913b9691322966fb77fe72269a0a2ec82/lang/c%2B%2B/CMakeLists.txt#L193
        target = "avrocpp" if self.options.shared else "avrocpp_s"
        self.cpp_info.components[target].libs = [target]
        self.cpp_info.components[target].requires = ["boost::boost", "snappy::snappy"]
        if self.options.shared:
            self.cpp_info.components[target].defines.append("AVRO_DYN_LINK")
