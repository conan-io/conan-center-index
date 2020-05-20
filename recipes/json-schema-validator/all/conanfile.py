import os
import glob
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class JsonSchemaValidatorConan(ConanFile):
    name = "json-schema-validator"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pboettch/json-schema-validator"
    description = "JSON schema validator for JSON for Modern C++ "
    topics = ("json-schema-validator", "modern-json",
              "schema-validation", "json")
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    short_paths = True
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
        min_vs_version = "16" if tools.Version(self.version) <= "2.0.0" else "14"
        min_cppstd = "17" if self.settings.compiler == "Visual Studio" and tools.Version(self.version) < "2.1.0" else "11"
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, min_cppstd)
            min_vs_version = "15" if tools.Version(self.version) <= "2.0.0" else "14"

        compilers = {"gcc": "5", "clang": "4",
                     "Visual Studio": min_vs_version, "apple-clang": "9"}
        min_version = compilers.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires c++{} support. The current compiler {} {} does not support it.".format(
                    self.name, min_cppstd, self.settings.compiler, self.settings.compiler.version))

    def requirements(self):
        self.requires("nlohmann_json/3.7.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(os.path.join("src", "json-schema.hpp"), dst=os.path.join("include", "nlohmann"), src=self._source_subfolder, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "nlohmann_json_schema_validator"
        self.cpp_info.names["cmake_find_package_multi"] = "nlohmann_json_schema_validator"
