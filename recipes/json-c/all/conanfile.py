from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.43.0"


class JSONCConan(ConanFile):
    name = "json-c"
    description = "JSON-C - A JSON implementation in C"
    topics = ("json-c", "json", "encoding", "decoding", "manipulation")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/json-c/json-c"
    license = "MIT"

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
    _cmake = None

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if tools.Version(self.version) <= "0.13.1" and \
           tools.cross_building(self) and self.settings.os != "Windows":
            host = tools.get_gnu_triplet(str(self.settings.os), str(self.settings.arch))
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                  "execute_process(COMMAND ./configure ",
                                  "execute_process(COMMAND ./configure --host %s " % host)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if tools.Version(self.version) >= "0.15":
            self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
            self._cmake.definitions["DISABLE_STATIC_FPIC"] = not self.options.get_safe("fPIC", True)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "json-c")
        self.cpp_info.set_property("cmake_target_name", "json-c::json-c")
        self.cpp_info.set_property("pkg_config_name", "json-c")
        self.cpp_info.libs = tools.collect_libs(self)
