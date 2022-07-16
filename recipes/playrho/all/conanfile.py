from conans import ConanFile, CMake, tools
import os
import functools

required_conan_version = ">=1.43.0"

class PlayrhoConan(ConanFile):
    name = "playrho"
    description = "Real-time oriented physics engine and library that's currently best suited for 2D games. "
    license = "zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/louis-langholtz/PlayRho/"
    topics = ("physics-engine", "collision-detection", "box2d")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
         "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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
            destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PLAYRHO_BUILD_SHARED"] = self.options.shared
        cmake.definitions["PLAYRHO_BUILD_STATIC"] = not self.options.shared
        cmake.definitions["PLAYRHO_INSTALL"] = True
        cmake.configure()
        return cmake

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "PlayRho", "CMakeLists.txt"),
            "target_compile_features(PlayRho PUBLIC cxx_std_17)",
            "target_compile_features(PlayRho_shared PUBLIC cxx_std_17)")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["PlayRho"]
        self.cpp_info.builddirs = os.path.join(self.package_folder, "lib", "PlayRho")

        self.cpp_info.set_property("cmake_file_name", "PlayRho")
        self.cpp_info.set_property("cmake_target_name", "PlayRho::PlayRho")

        #  TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "PlayRho"
        self.cpp_info.filenames["cmake_find_package_multi"] = "PlayRho"
        self.cpp_info.names["cmake_find_package"] = "PlayRho"
        self.cpp_info.names["cmake_find_package_multi"] = "PlayRho"
