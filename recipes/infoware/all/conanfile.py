from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class InfowareConan(ConanFile):
    name = "infoware"
    license = "CC0 1.0 Universal"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("infoware", "hardware")
    homepage = "https://github.com/ThePhD/infoware"
    description = "C++ Library for pulling system and hardware information, without hitting the command line."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "shared": [True, False]
    }
    default_options = {"fPIC": True, "shared": True}
    exports_sources = ["CMakeLists.txt"]
    generators = ["cmake", "cmake_find_package", "cmake_find_package_multi"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

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
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.libs.append(self.name + ("d" if self.settings.build_type == "Debug" else ""))

        self.cpp_info.names["cmake_find_package"] = self.name
        self.cpp_info.names["cmake_find_package_multi"] = self.name
