from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os.path


class KittenConan(ConanFile):
    name = "kitten"
    description = "A small C++ library inspired by Category Theory focused on functional composition."
    homepage = "https://github.com/rvarago/kitten"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    topics = ("category-theory", "composition", "monadic-interface", "declarative-programming")
    no_copy_source = True
    settings = "compiler"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _has_support_for_cpp17(self):
        supported_compilers = [("apple-clang", 10), ("clang", 5), ("gcc", 7), ("Visual Studio", 15.7)]
        compiler, version = self.settings.compiler, Version(self.settings.compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.configure(source_folder=self._source_subfolder,
                        build_folder=self._build_subfolder)
        return cmake

    def configure(self):
        if not self._has_support_for_cpp17():
            raise ConanInvalidConfiguration("Kitten requires support for C++17")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_id(self):
        self.info.header_only()
