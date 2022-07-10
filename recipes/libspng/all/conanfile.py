from conans import ConanFile, CMake, tools
import os
import functools

required_conan_version = ">=1.43.0"

class LibspngConan(ConanFile):
    name = "libspng"
    description = "Simple, modern libpng alternative "
    topics = ("png", "libpng", "spng")
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/randy408/libspng/"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_miniz": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_miniz": False,
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_miniz:
            self.requires("miniz/2.2.0")
        else:
            self.requires("zlib/1.2.12")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SPNG_SHARED"] = self.options.shared
        cmake.definitions["SPNG_STATIC"] = not self.options.shared
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["CMAKE_C_FLAGS"] = "-DSPNG_USE_MINIZ" if self.options.with_miniz else ""
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "spng")
        self.cpp_info.set_property("cmake_target_name", "spng::spng")

        self.cpp_info.names["cmake_find_package"] = "spng"
        self.cpp_info.names["cmake_find_package_multi"] = "spng"

        if not self.options.shared:
            self.cpp_info.defines = ["SPNG_STATIC"]

        self.cpp_info.libs = ["spng"] if self.options.shared else ["spng_static"]
        if self.settings.os in ["Linux", "Android", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
