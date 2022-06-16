from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools

required_conan_version = ">=1.43.0"


class SamariumConan(ConanFile):
    name = "samarium"
    description = "2-D physics simulation library"
    homepage = "https://strangequark1041.github.io/samarium/"
    url = "https://github.com/conan-io/conan-center-index/"
    license = "MIT"
    topics = ("cpp20", "physics", "2d", "simulation")

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    generators = "cmake", "cmake_find_package_multi"
    requires = "fmt/8.1.1", "sfml/2.5.1"

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11.0",
            "Visual Studio": "16.9",
            "clang": "13",
            "apple-clang": "13",
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)

        # from https://github.com/conan-io/conan-center-index/blob/eb92a57e0ea55c9d23b401797fa7d9544a343a4d/recipes/jfalcou-eve/all/conanfile.py#L38
        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(
                "{} {} requires C++20. Your compiler is unknown. Assuming it supports C++20.".format(self.name, self.version))
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                "{} {} requires C++20, which your compiler does not support.".format(self.name, self.version))

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["samarium"]
        self.cpp_info.filenames["cmake_find_package"] = "SAMARIUM"
        self.cpp_info.filenames["cmake_find_package_multi"] = "samarium"
        self.cpp_info.names["cmake_find_package"] = "SAMARIUM"
        self.cpp_info.names["cmake_find_package_multi"] = "samarium"

        self.cpp_info.set_property("cmake_file_name", "SAMARIUM")
        self.cpp_info.set_property("cmake_target_name", "samarium::samarium") 
