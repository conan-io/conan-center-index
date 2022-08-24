from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class KittenConan(ConanFile):
    name = "kitten"
    description = "A small C++ library inspired by Category Theory focused on functional composition."
    homepage = "https://github.com/rvarago/kitten"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    topics = ("category-theory", "composition", "monadic-interface", "declarative-programming")

    settings = "os", "arch", "compiler", "build_type"

    no_copy_source = True
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "7",
            "clang": "5",
            "Visual Studio": "15.7",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if min_version and loose_lt_semver(str(self.settings.compiler.version), min_version):
            raise ConanInvalidConfiguration(
                "{} requires C++17, which your compiler does not support.".format(self.name)
            )

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "kitten")
        self.cpp_info.set_property("cmake_target_name", "rvarago::kitten")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "kitten"
        self.cpp_info.filenames["cmake_find_package_multi"] = "kitten"
        self.cpp_info.names["cmake_find_package"] = "rvarago"
        self.cpp_info.names["cmake_find_package_multi"] = "rvarago"
        self.cpp_info.components["libkitten"].names["cmake_find_package"] = "kitten"
        self.cpp_info.components["libkitten"].names["cmake_find_package_multi"] = "kitten"
        self.cpp_info.components["libkitten"].set_property("cmake_target_name", "rvarago::kitten")
