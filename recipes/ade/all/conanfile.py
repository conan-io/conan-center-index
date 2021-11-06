from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class AdeConan(ConanFile):
    name = "ade"
    license = "Apache-2.0"
    homepage = "https://github.com/opencv/ade"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Graph construction, manipulation, and processing framework"
    topics = ("graphs", "opencv")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        # FIXME opencv expects this target to be "ade" but conan will bind it as ade::ade
        self.cpp_info.names["cmake_find_package"] = "ade"
        self.cpp_info.names["cmake_find_package_multi"] = "ade"
        self.cpp_info.libs = ["ade"]
