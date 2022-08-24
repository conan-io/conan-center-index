from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class AbsentConan(ConanFile):
    name = "absent"
    description = (
        "A small C++17 library meant to simplify the composition of nullable "
        "types in a generic, type-safe, and declarative way"
    )
    homepage = "https://github.com/rvarago/absent"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    topics = ("nullable-types", "composition", "monadic-interface", "declarative-programming")
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
            "Visual Studio": "15.7",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                "{} requires C++17, which your compiler does not support.".format(self.name)
            )

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "absent")
        self.cpp_info.set_property("cmake_target_name", "rvarago::absent")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["absentlib"].bindirs = []
        self.cpp_info.components["absentlib"].frameworkdirs = []
        self.cpp_info.components["absentlib"].libdirs = []
        self.cpp_info.components["absentlib"].resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "absent"
        self.cpp_info.filenames["cmake_find_package_multi"] = "absent"
        self.cpp_info.names["cmake_find_package"] = "rvarago"
        self.cpp_info.names["cmake_find_package_multi"] = "rvarago"
        self.cpp_info.components["absentlib"].names["cmake_find_package"] = "absent"
        self.cpp_info.components["absentlib"].names["cmake_find_package_multi"] = "absent"
        self.cpp_info.components["absentlib"].set_property("cmake_target_name", "rvarago::absent")
