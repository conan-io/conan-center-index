import os
import glob
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class TinyDnnConan(ConanFile):
    name = "tiny-dnn"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tiny-dnn/tiny-dnn"
    description = "tiny-dnn is a C++14 implementation of deep learning."
    topics = ("header-only", "deep-learning", "embedded", "iot", "computational")
    settings = "compiler", "os"
    options = {"with_tbb": [True, False]}
    default_options = {"with_tbb": False}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("cereal/1.3.0")
        self.requires("stb/20200203")
        if self.options.with_tbb:
            self.requires("tbb/2020.3")

    def configure(self):
        minimal_cpp_standard = "14"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "14"
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "{} recipe lacks information about the {} compiler standard version support".format(self.name, compiler))
            self.output.warn(
                "{} requires a compiler that supports at least C++{}".format(self.name, minimal_cpp_standard))
            return
        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("{} requires a compiler that supports at least C++{}".format(self.name, minimal_cpp_standard))

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("tiny-dnn-*")[0], self._source_subfolder)

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "tiny_dnn", "util", "image.h"), "third_party/", "")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.definitions["USE_TBB"] = self.options.with_tbb
        cmake.definitions["USE_GEMMLOWP"] = False
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "tinydnn"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tinydnn"
        self.cpp_info.names["cmake_find_package"] = "TinyDNN"
        self.cpp_info.names["cmake_find_package_multi"] = "TinyDNN"
        self.cpp_info.components["tinydnn"].names["cmake_find_package"] = "tiny_dnn"
        self.cpp_info.components["tinydnn"].names["cmake_find_package_multi"] = "tiny_dnn"
        self.cpp_info.components["tinydnn"].requires = ["cereal::cereal", "stb::stb"]
        if self.settings.os == "Linux":
            self.cpp_info.components["tinydnn"].system_libs = ["pthread"]
        if self.options.with_tbb:
            self.cpp_info.components["tinydnn"].requires.append("tbb::tbb")
            self.cpp_info.components["tinydnn"].defines = ["CNN_USE_TBB=1"]
