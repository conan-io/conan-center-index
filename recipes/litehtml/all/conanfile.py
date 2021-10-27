import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class LitehtmlConan(ConanFile):
    name = "litehtml"
    description = "litehtml is the lightweight HTML rendering engine with CSS2/CSS3 support."
    license = "BSD3"
    topics = ("render engine", "html", "parser")
    homepage = "https://github.com/litehtml/litehtml"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _min_cppstd(self):
        return "11"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.components["litehtml_core"].names["cmake_find_package"] = "litehtml"
        self.cpp_info.components["litehtml_core"].names["cmake_find_package_multi"] = "litehtml"
        self.cpp_info.components["litehtml_core"].libs = ["litehtml"]
        self.cpp_info.components["litehtml_core"].requires = ["gumbo"]
        
        self.cpp_info.components["gumbo"].names["cmake_find_package"] = "gumbo"
        self.cpp_info.components["gumbo"].names["cmake_find_package_multi"] = "gumbo"
        self.cpp_info.components["gumbo"].libs = ["gumbo"]

