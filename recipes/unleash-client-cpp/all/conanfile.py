from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class UnleashConan(ConanFile):
    name = "unleash-client-cpp"
    homepage = "https://github.com/aruizs/unleash-client-cpp/"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Unleash Client SDK for C++ projects."
    topics = ("unleash", "feature", "flag", "toggle")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_min_version(self):
        return {
            "Visual Studio": "15",  # Should we check toolset?
            "gcc": "7",
            "clang": "4.0",
            "apple-clang": "3.8",
            "intel": "17",
        }

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
        self.requires("cpr/1.7.2")
        self.requires("nlohmann_json/3.10.5")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        min_version = self._compilers_min_version.get(str(self.settings.compiler), False)
        if min_version and loose_lt_semver(str(self.settings.compiler.version), min_version):
            raise ConanInvalidConfiguration(
                "{} requires C++{}, which your compiler does not support.".format(self.name, self._min_cppstd)
            )

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_TESTING"] = False
        self._cmake.definitions["ENABLE_TEST_COVERAGE"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "unleash")
        self.cpp_info.set_property("cmake_target_name", "unleash::unleash")
        self.cpp_info.libs = ["unleash"]

        self.cpp_info.names["cmake_find_package"] = "unleash"
        self.cpp_info.names["cmake_find_package_multi"] = "unleash"

