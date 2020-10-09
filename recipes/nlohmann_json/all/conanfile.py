from conans import ConanFile, tools, CMake
import os


class NlohmannJsonConan(ConanFile):
    name = "nlohmann_json"
    homepage = "https://github.com/nlohmann/json"
    description = "JSON for Modern C++ parser and generator."
    topics = ("conan", "jsonformoderncpp",
              "nlohmann_json", "json", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "multiple_headers": [True, False],
        "implicit_conversions": [True, False],
    }
    default_options = {
        "multiple_headers": False,
        "implicit_conversions": True,
    }

    _cmake = None

    @property
    def _can_disable_implicit_conversions(self):
        return tools.Version(self.version) >= "3.9.0"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if not self._can_disable_implicit_conversions:
            del self.options.implicit_conversions

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "json-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["JSON_BuildTests"] = False
        self._cmake.definitions["JSON_MultipleHeaders"] = self.options.multiple_headers
        if self._can_disable_implicit_conversions:
            self._cmake.definitions["JSON_ImplicitConversions"] = self.options.implicit_conversions

        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

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

    def package_id(self):
        self.info.settings.clear()

    def package_info(self):
        if self._can_disable_implicit_conversions:
            self.cpp_info.defines = ["JSON_USE_IMPLICIT_CONVERSIONS=%s" % int(bool(self.options.implicit_conversions))]
