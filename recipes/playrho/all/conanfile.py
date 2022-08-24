from conan import ConanFile, tools
from conans import CMake
from conans.tools import ConanInvalidConfiguration
import os
import functools

required_conan_version = ">=1.43.0"

class PlayrhoConan(ConanFile):
    name = "playrho"
    description = "Real-time oriented physics engine and library that's currently best suited for 2D games. "
    license = "Zlib"
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
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _compilers_minimum_versions(self):
        return {
            "gcc": "8",
            "Visual Studio": "16",
            "clang": "7",
            "apple-clang": "12",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 17)

        compilers_minimum_version = self._compilers_minimum_versions
        minimum_version = compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.scm.Version(self, self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
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
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "PlayRho"))

    def package_info(self):
        self.cpp_info.libs = ["PlayRho"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        self.cpp_info.set_property("cmake_file_name", "PlayRho")
        self.cpp_info.set_property("cmake_target_name", "PlayRho::PlayRho")

        #  TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "PlayRho"
        self.cpp_info.filenames["cmake_find_package_multi"] = "PlayRho"
        self.cpp_info.names["cmake_find_package"] = "PlayRho"
        self.cpp_info.names["cmake_find_package_multi"] = "PlayRho"
