from conan import ConanFile, tools
from conan.tools.cmake import CMake

required_conan_version = ">=1.33.0"


class TinyregexcConan(ConanFile):
    name = "tiny-regex-c"
    description = "Small and portable Regular Expression (regex) library written in C."
    license = "Unlicense"
    topics = ("conan", "tiny-regex-c", "regex")
    homepage = "https://github.com/kokke/tiny-regex-c"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "dot_matches_newline": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "dot_matches_newline": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

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

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["RE_DOT_MATCHES_NEWLINE"] = self.options.dot_matches_newline
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["tiny-regex-c"]
        self.cpp_info.defines = ["RE_DOT_MATCHES_NEWLINE={}".format("1" if self.options.dot_matches_newline else "0")]
