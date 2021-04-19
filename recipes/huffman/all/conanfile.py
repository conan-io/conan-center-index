from conans import ConanFile, CMake, tools
import os


class HuffmanConan(ConanFile):
    name = "huffman"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/drichardson/huffman"
    description = "huffman encoder/decoder"
    topics = ["huffman", "conan"]
    license = "Unlicense"
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {'shared': False,
                       'fPIC': True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "huffman-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs.append("huffman")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
