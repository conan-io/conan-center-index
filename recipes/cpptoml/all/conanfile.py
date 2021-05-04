from conans import ConanFile, tools, CMake
import os
import glob


class CppTomlConan(ConanFile):
    name = "cpptoml"
    description = "cpptoml is a header-only library for parsing TOML "
    topics = ("conan","toml","cpptoml")
    license = " MIT License "
    homepage = "https://github.com/skystrife/cpptoml"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "build_examples": [True, False]
    }
    default_options = {
        "build_examples": False
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"
    
    @property
    def _build_subfolder(self):
        return "build_subfolder"
        
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        tools.replace_in_file("{0}/CMakeLists.txt".format(extracted_dir),
            "list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/deps/meta-cmake)",
            "")
        os.rename(extracted_dir,self._source_subfolder)
        
    def build(self):
        cmake = CMake(self)
        cmake.definitions["CPPTOML_BUILD_EXAMPLES"] = self.options.build_examples
        cmake.configure(build_folder=self._build_subfolder,source_folder=self._source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)

    def package_id(self):
        self.info.header_only()