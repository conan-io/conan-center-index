from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os.path

required_conan_version = ">=1.28.0"

class KittenConan(ConanFile):
    name = "kitten"
    description = "A small C++ library inspired by Category Theory focused on functional composition."
    homepage = "https://github.com/rvarago/kitten"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    topics = ("category-theory", "composition", "monadic-interface", "declarative-programming")
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    no_copy_source = True
    settings = "os", "compiler", "build_type", "arch"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _has_support_for_cpp17(self):
        supported_compilers = [("apple-clang", 10), ("clang", 5), ("gcc", 7), ("Visual Studio", 15.7)]
        compiler, version = self.settings.compiler, Version(self.settings.compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 17)
        if not self._has_support_for_cpp17():
            raise ConanInvalidConfiguration("Kitten requires support for C++17")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

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
        self.cpp_info.filenames["cmake_find_package"] = "kitten"
        self.cpp_info.filenames["cmake_find_package_multi"] = "kitten"
        self.cpp_info.names["cmake_find_package"] = "rvarago"
        self.cpp_info.names["cmake_find_package_multi"] = "rvarago"
        self.cpp_info.components["libkitten"].names["cmake_find_package"] = "kitten"
        self.cpp_info.components["libkitten"].names["cmake_find_package_multi"] = "kitten"
