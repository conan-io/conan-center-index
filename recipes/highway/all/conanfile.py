from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import functools

required_conan_version = ">=1.33.0"

class HighwayConan(ConanFile):
    name = "highway"
    description = "Performance-portable, length-agnostic SIMD with runtime " \
                  "dispatch"
    topics = ("highway", "simd")
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/highway"
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

    @property
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "8",
            "clang": "7",
        }

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if tools.scm.Version(self, self.version) < "0.16.0":
            del self.options.shared
        elif self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, self._minimum_cpp_standard)
        minimum_version = self._minimum_compilers_version.get(
                                                   str(self.settings.compiler))
        if not minimum_version:
            self.output.warn(
                "{} recipe lacks information about the {} compiler support."
                .format(self.name, self.settings.compiler))
        elif tools.scm.Version(self, self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "{} requires a {} version >= {}"
                .format(self.name, self.settings.compiler,
                        self.settings.compiler.version))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # Honor fPIC option
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.files.replace_in_file(self, cmakelists,
                              "set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)", "")
        tools.files.replace_in_file(self, cmakelists,
                              "set_property(TARGET hwy PROPERTY "
                              "POSITION_INDEPENDENT_CODE ON)", "")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["HWY_ENABLE_EXAMPLES"] = False
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libhwy"

        self.cpp_info.libs = ["hwy"]
        if tools.scm.Version(self, self.version) >= "0.12.1":
            self.cpp_info.libs.append("hwy_contrib")
        if tools.scm.Version(self, self.version) >= "0.15.0":
            self.cpp_info.libs.append("hwy_test")
        if tools.scm.Version(self, self.version) >= "0.16.0":
            self.cpp_info.defines.append("HWY_SHARED_DEFINE" if self.options.shared else "HWY_STATIC_DEFINE")
