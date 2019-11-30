from conans import ConanFile, CMake, tools
import os


class Re2Conan(ConanFile):
    name = "re2"
    description = "Fast, safe, thread-friendly regular expression library"
    topics = ("conan", "re2", "regex")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/re2"
    license = "BSD-3-Clause"

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False, 
        "fPIC": True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def source(self):
        version_src = self.conan_data["sources"][self.version].copy()
        del version_src["compressed_dirname"]
        tools.get(**version_src)
        os.rename(self.conan_data["sources"][self.version]["compressed_dirname"], self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["RE2_BUILD_TESTING"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
