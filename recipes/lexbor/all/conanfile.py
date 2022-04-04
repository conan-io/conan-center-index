from conans import ConanFile, CMake, tools
import functools

required_conan_version = ">=1.43.0"

class LexborConan(ConanFile):
    name = "lexbor"
    license = "Apache-2.0"
    homepage = "https://github.com/lexbor/lexbor/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Lexbor is development of an open source HTML Renderer library"
    topics = ("html5", "css", "parser", "renderer")
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", ]
    options = {
        "shared": [True, False], 
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False, 
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["LEXBOR_BUILD_SHARED"] = self.options.shared
        cmake.definitions["LEXBOR_BUILD_STATIC"] = not self.options.shared
        cmake.definitions["LEXBOR_TESTS_CPP"] = False
        # TODO: enable build_separately option
        cmake.definitions["LEXBOR_BUILD_SEPARATELY"] = False
        cmake.definitions["LEXBOR_INSTALL_HEADERS"] = True

        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        target = "lexbor" if self.options.shared else "lexbor_static"
        self.cpp_info.set_property("cmake_file_name", "lexbor")
        self.cpp_info.set_property("cmake_target_name", "lexbor::{}".format(target))
        self.cpp_info.components["_lexbor"].libs = [target]

        self.cpp_info.names["cmake_find_package"] = "lexbor"
        self.cpp_info.names["cmake_find_package_multi"] = "lexbor"
        self.cpp_info.components["_lexbor"].names["cmake_find_package"] = target
        self.cpp_info.components["_lexbor"].names["cmake_find_package_multi"] = target
        self.cpp_info.components["_lexbor"].set_property("cmake_target_name", "lexbor::{}".format(target))
