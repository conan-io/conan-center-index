import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class FclConan(ConanFile):
    name = "fcl"
    description = "C++11 library for performing three types of proximity " \
                  "queries on a pair of geometric models composed of triangles."
    license = "BSD-3-Clause"
    topics = ("conan", "fcl", "geometry", "collision")
    homepage = "https://github.com/flexible-collision-library/fcl"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_octomap": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_octomap": True
    }

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

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("{0} {1} doesn't properly support shared lib on Windows".format(self.name,
                                                                                                            self.version))

    def requirements(self):
        self.requires.add("eigen/3.3.7")
        self.requires.add("libccd/2.1")
        if self.options.with_octomap:
            self.requires.add("octomap/1.9.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FCL_ENABLE_PROFILING"] = False
        self._cmake.definitions["FCL_TREAT_WARNINGS_AS_ERRORS"] = False
        self._cmake.definitions["FCL_HIDE_ALL_SYMBOLS"] = False
        self._cmake.definitions["FCL_STATIC_LIBRARY"] = not self.options.shared
        self._cmake.definitions["FCL_USE_X64_SSE"] = False # Let consumer decide to add relevant compile options, ftl doesn't have simd intrinsics
        self._cmake.definitions["FCL_USE_HOST_NATIVE_ARCH"] = False
        self._cmake.definitions["FCL_USE_SSE"] = False
        self._cmake.definitions["FCL_COVERALLS"] = False
        self._cmake.definitions["FCL_COVERALLS_UPLOAD"] = False
        self._cmake.definitions["FCL_WITH_OCTOMAP"] = self.options.with_octomap
        if self.options.with_octomap:
            octomap_major, octomap_minor, octomap_patch = self.deps_cpp_info["octomap"].version.split(".")
            self._cmake.definitions["OCTOMAP_MAJOR_VERSION"] = octomap_major
            self._cmake.definitions["OCTOMAP_MINOR_VERSION"] = octomap_minor
            self._cmake.definitions["OCTOMAP_PATCH_VERSION"] = octomap_patch
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "CMake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
