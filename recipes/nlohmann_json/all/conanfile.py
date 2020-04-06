from conans import ConanFile, tools, CMake
import os


class NlohmannJsonConan(ConanFile):
    name = "nlohmann_json"
    homepage = "https://github.com/nlohmann/json"
    description = "JSON for Modern C++ parser and generator."
    topics = ("conan", "jsonformoderncpp", "nlohmann_json", "json", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    license = "MIT"
    options = {
        "multiple_headers": [True, False]
    }
    default_options = {
        "multiple_headers": False
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "json-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["JSON_BuildTests"] = False
        cmake.definitions["JSON_MultipleHeaders"] = self.options.multiple_headers
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))
        try:
            os.remove(os.path.join(self.package_folder, "nlohmann_json.natvis"))
        except FileNotFoundError:
            pass
