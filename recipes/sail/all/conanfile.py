from conans import ConanFile, CMake, tools

required_conan_version = ">=1.43.0"

class SAILConan(ConanFile):
    name = "sail"
    version = "0.9.0"
    author = "Dmitry Baryshev"
    description = "The missing small and fast image decoding library for humans (not for machines)"
    url = "https://github.com/HappySeaFox/sail.git"
    homepage = "https://sail.software"
    topics = ( "image", "encoding", "decoding", "graphics" )
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    requires = "giflib/5.2.1", "libavif/0.9.3", "libjpeg/9d", "libpng/1.6.37", "libtiff/4.3.0", "libwebp/1.2.2"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
    }
    #generators = "cmake" #, "cmake_find_package_multi"
    exports_sources = "CMakeLists.txt"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["SAIL_BUILD_EXAMPLES"] = False
        self._cmake.definitions["SAIL_BUILD_TESTS"]    = False
        self._cmake.definitions["SAIL_COMBINE_CODECS"] = True
        self._cmake.configure(build_folder=self._build_subfolder)

        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt",       src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE.INIH.txt",  src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE.MUNIT.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"]       = "Sail"
        self.cpp_info.names["cmake_find_package_multi"] = "Sail"
        self.cpp_info.components["C++"].names["cmake_find_package"]       = "SailC++"
        self.cpp_info.components["C++"].names["cmake_find_package_multi"] = "SailC++"
