from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class PolylineencoderConan(ConanFile):
    name = "polylineencoder"
    description = "Google Encoded Polyline Algorithm Format library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/vahancho/polylineencoder"
    license = "MIT"
    topics = ("conan", "gepaf", "encoded-polyline", "google-polyline")
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/*"
    _cmake = None
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs.append("polylineencoder")
