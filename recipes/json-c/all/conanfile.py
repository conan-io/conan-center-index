from conans import ConanFile, CMake, tools
import os


class JSONCConan(ConanFile):
    name = "json-c"
    description = "JSON-C - A JSON implementation in C"
    topics = ("conan", "json-c", "json", "encoding", "decoding", "manipulation")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/json-c/json-c"
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        extracted_dir = self.name + "-" + url[url.rfind("/")+1:url.find(".tar.gz")]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        if tools.Version(self.version) <= "0.13.1" and \
           tools.cross_building(self.settings) and self.settings.os != "Windows":
            host = tools.get_gnu_triplet(str(self.settings.os), str(self.settings.arch))
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                  "execute_process(COMMAND ./configure ",
                                  "execute_process(COMMAND ./configure --host %s " % host)

        self._cmake = CMake(self)

        if tools.Version(self.version) >= "0.15":
            self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
            self._cmake.definitions["DISABLE_STATIC_FPIC"] = not self.options.get_safe("fPIC", True)

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "json-c"
        self.cpp_info.names["cmake_find_package_multi"] = "json-c"
        self.cpp_info.names["pkg_config"] = "json-c"
