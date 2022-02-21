from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class RapidYAMLConan(ConanFile):
    name = "rapidyaml"
    description = "a library to parse and emit YAML, and do it fast."
    topics = ("yaml", "parser", "emitter")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/biojppm/rapidyaml"
    license = "MIT",
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_default_callbacks": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_default_callbacks": True,
    }
    generators = "cmake", "cmake_find_package_multi"

    _compiler_required_cpp11 = {
        "Visual Studio": "13",
        "gcc": "6",
        "clang": "4",
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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

    def requirements(self):
        self.requires("c4core/0.1.8")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

        minimum_version = self._compiler_required_cpp11.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++11, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{0} requires C++11. Your compiler is unknown. Assuming it supports C++11.".format(self.name))

        if self.settings.compiler == "clang" and self.settings.compiler.get_safe("libcxx") == "libc++":
            raise ConanInvalidConfiguration("{} doesn't support clang with libc++".format(self.name))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["RYML_DEFAULT_CALLBACKS"] = self.options.with_default_callbacks
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "include"), "*.natvis")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ryml")
        self.cpp_info.set_property("cmake_target_name", "ryml::ryml")
        self.cpp_info.libs = ["ryml"]

        self.cpp_info.names["cmake_find_package"] = "ryml"
        self.cpp_info.names["cmake_find_package_multi"] = "ryml"
