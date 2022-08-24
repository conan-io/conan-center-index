from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class TinyDnnConan(ConanFile):
    name = "tiny-dnn"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tiny-dnn/tiny-dnn"
    description = "tiny-dnn is a C++14 implementation of deep learning."
    topics = ("header-only", "deep-learning", "embedded", "iot", "computational")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_tbb": [True, False],
    }
    default_options = {
        "with_tbb": False,
    }

    exports_sources = "CMakeLists.txt"
    # TODO: if you move this recipe to CMakeDeps, be aware that tiny-dnn
    #       relies on CMake variables which are not defined in CMakeDeps, only
    #       in cmake_find_package. So patch it before.
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _min_compilers_version(self):
        return {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "14"
        }

    def requirements(self):
        self.requires("cereal/1.3.1")
        self.requires("stb/cci.20210713")
        if self.options.with_tbb:
            self.requires("onetbb/2020.3")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, self._min_cppstd)

        compiler = str(self.settings.compiler)
        version = tools.Version(self.settings.compiler.version)
        if compiler in self._min_compilers_version and version < self._min_compilers_version[compiler]:
            raise ConanInvalidConfiguration(
                "{} requires a compiler that supports at least C++{}".format(
                    self.name, self._min_cppstd,
                )
            )

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        tools.files.replace_in_file(self, 
            os.path.join(self._source_subfolder, "tiny_dnn", "util", "image.h"),
            "third_party/", "",
        )

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.definitions["USE_TBB"] = self.options.with_tbb
        cmake.definitions["USE_GEMMLOWP"] = False
        cmake.configure()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tinydnn")
        self.cpp_info.set_property("cmake_target_name", "TinyDNN::tiny_dnn")
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["tinydnn"].system_libs = ["pthread"]
        if self.options.with_tbb:
            self.cpp_info.components["tinydnn"].defines = ["CNN_USE_TBB=1"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "tinydnn"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tinydnn"
        self.cpp_info.names["cmake_find_package"] = "TinyDNN"
        self.cpp_info.names["cmake_find_package_multi"] = "TinyDNN"
        self.cpp_info.components["tinydnn"].names["cmake_find_package"] = "tiny_dnn"
        self.cpp_info.components["tinydnn"].names["cmake_find_package_multi"] = "tiny_dnn"
        self.cpp_info.components["tinydnn"].set_property("cmake_target_name", "TinyDNN::tiny_dnn")
        self.cpp_info.components["tinydnn"].requires = ["cereal::cereal", "stb::stb"]
        if self.options.with_tbb:
            self.cpp_info.components["tinydnn"].requires.append("onetbb::onetbb")
