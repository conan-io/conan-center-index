from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.43.0"


class LibunifexConan(ConanFile):
    name = "libunifex"
    license = ("Apache-2.0", "LLVM-exception")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebookexperimental/libunifex"
    description = "A prototype implementation of the C++ sender/receiver async programming model"
    topics = ("async", "cpp")

    settings = "os", "arch", "compiler", "build_type"

    generators = "cmake", "cmake_find_package_multi"
    no_copy_source = True
    exports_sources = ["CMakeLists.txt"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "16",
            "clang": "10",
            "apple-clang": "11",
        }

    @property
    def _minimum_standard(self):
        return "17"

    # FIXME: Add support for liburing
    # def requirements(self):
        # TODO: Make an option to opt-out of liburing for old kernel versions
        # if self.settings.os == "Linux":
        #    self.requires("liburing/2.1")

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
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "unifex")
        self.cpp_info.set_property("cmake_target_name", "unifex::unifex")
        self.cpp_info.set_property("pkg_config_name", "unifex")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "unifex"
        self.cpp_info.filenames["cmake_find_package_multi"] = "unifex"
        self.cpp_info.names["cmake_find_package"] = "unifex"
        self.cpp_info.names["cmake_find_package_multi"] = "unifex"
        self.cpp_info.names["pkg_config"] = "unifex"
        self.cpp_info.components["unifex"].names["cmake_find_package"] = "unifex"
        self.cpp_info.components["unifex"].names["cmake_find_package_multi"] = "unifex"
        self.cpp_info.components["unifex"].set_property(
            "cmake_target_name", "unifex::unifex")
        self.cpp_info.components["unifex"].libs = ["unifex"]

        if self.settings.os == "Linux":
            self.cpp_info.components["unifex"].system_libs = ["pthread"]
        #    self.cpp_info.components["unifex"].requires.append(
        #        "liburing::liburing")
