from conans import ConanFile, CMake, tools
from conan.tools.microsoft import is_msvc
import functools

required_conan_version = ">=1.43.0"

class LexborConan(ConanFile):
    name = "lexbor"
    description = "Lexbor is development of an open source HTML Renderer library"
    topics = ("html5", "css", "parser", "renderer")
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lexbor/lexbor/"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False],
        "build_separately": [True, False],
    }
    default_options = {
        "shared": False, 
        "fPIC": True,
        "build_separately": False,
    }
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", ]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def validate(self):
        # static build on Windows will be support by future release. (https://github.com/lexbor/lexbor/issues/69)
        if str(self.version) == "2.1.0" and self.options.shared == False and (is_msvc(self) or self._is_mingw):
            raise tools.ConanInvalidConfiguration("{}/{} doesn't support static build on Windows(please use cci.20220301).".format(self.name, self.version))

        if self.options.build_separately:
            raise tools.ConanInvalidConfiguration("{}/{} doesn't support build_separately option(yet).".format(self.name, self.version))

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
        cmake.definitions["LEXBOR_BUILD_SEPARATELY"] = self.options.build_separately
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
        self.cpp_info.names["cmake_find_package"] = "lexbor"
        self.cpp_info.names["cmake_find_package_multi"] = "lexbor"

        self.cpp_info.components["_lexbor"].set_property("cmake_target_name", "lexbor::{}".format(target))
        self.cpp_info.components["_lexbor"].names["cmake_find_package"] = target
        self.cpp_info.components["_lexbor"].names["cmake_find_package_multi"] = target

        self.cpp_info.components["_lexbor"].libs = [target]
        self.cpp_info.components["_lexbor"].defines = ["LEXBOR_BUILD_SHARED" if self.options.shared else "LEXBOR_BUILD_STATIC"]
