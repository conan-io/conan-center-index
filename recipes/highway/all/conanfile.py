from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class HighwayConan(ConanFile):
    name = "highway"
    description = "Performance-portable, length-agnostic SIMD with runtime " \
                  "dispatch"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/highway"
    topics = ("highway", "simd")

    settings = "os", "compiler", "build_type", "arch"

    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "8",
            "clang": "7",
        }

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        minimum_version = self._minimum_compilers_version.get(
                                                    str(self.settings.compiler))
        if not minimum_version:
            self.output.warn(
                "{} recipe lacks information about the {} compiler support."
                .format(self.name, self.settings.compiler))
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "{} requires a {} version >= {}"
                .format(self.name, self.settings.compiler,
                        self.settings.compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Highway"
        self.cpp_info.names["cmake_find_package_multi"] = "Highway"
        self.cpp_info.libs = tools.collect_libs(self)
