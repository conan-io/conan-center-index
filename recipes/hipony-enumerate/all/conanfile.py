from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.43.0"


class HiponyEnumerateConan(ConanFile):
    name = "hipony-enumerate"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hipony/enumerate"
    description = "C++11 compatible version of enumerate"
    topics = ("enumerate", "header-only", "cpp",
              "constexpr", "cpp17", "cpp11", "tuples")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "aggregates": [True, False],
    }
    default_options = {
        "aggregates": False,
    }

    generators = "cmake", "cmake_find_package_multi"
    no_copy_source = True
    exports_sources = ["CMakeLists.txt"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8" if self.options.aggregates else "6",
            "Visual Studio": "16" if self.options.aggregates else "14",
            "clang": "5.0" if self.options.aggregates else "3.9",
            "apple-clang": "10",
        }

    @property
    def _minimum_standard(self):
        return "17" if self.options.aggregates else "11"

    def requirements(self):
        if self.options.aggregates:
            self.requires("pfr/2.0.3")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(
                self, self._minimum_standard)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(
                "{0} {1} requires C++{2}. Your compiler is unknown. Assuming it supports C++{2}."
                .format(self.name, self.version, self._minimum_standard))
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                "{} {} requires C++{}, which your compiler does not support."
                .format(self.name, self.version, self._minimum_standard))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["HIPONY_ENUMERATE_AGGREGATES_ENABLED"] = self.options.aggregates
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "hipony-enumerate")
        self.cpp_info.set_property("cmake_target_name", "hipony::enumerate")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        if self.options.aggregates:
            self.cpp_info.components["enumerate"].defines.append(
                "HIPONY_ENUMERATE_AGGREGATES_ENABLED")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "hipony-enumerate"
        self.cpp_info.filenames["cmake_find_package_multi"] = "hipony-enumerate"
        self.cpp_info.names["cmake_find_package"] = "hipony"
        self.cpp_info.names["cmake_find_package_multi"] = "hipony"
        self.cpp_info.components["enumerate"].names["cmake_find_package"] = "enumerate"
        self.cpp_info.components["enumerate"].names["cmake_find_package_multi"] = "enumerate"
        self.cpp_info.components["enumerate"].set_property("cmake_target_name", "hipony::enumerate")
        if self.options.aggregates:
            self.cpp_info.components["enumerate"].requires.append("pfr::pfr")
