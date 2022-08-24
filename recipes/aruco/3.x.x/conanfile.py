from conans import ConanFile, tools, CMake
import functools
import os

required_conan_version = ">=1.36.0"


class ArucoConan(ConanFile):
    name = "aruco"
    description = "Augmented reality library based on OpenCV "
    topics = ("aruco", "augmented reality")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.uco.es/investiga/grupos/ava/node/26"
    license = "GPL-3.0-only"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [False, True],
        "fPIC": [False, True],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"

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
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("opencv/4.5.5")
        self.requires("eigen/3.4.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ARUCO_DEVINSTALL"] = True
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["BUILD_GLSAMPLES"] = False
        cmake.definitions["BUILD_UTILS"] = False
        cmake.definitions["BUILD_DEBPACKAGE"] = False
        cmake.definitions["BUILD_SVM"] = False
        cmake.definitions["INSTALL_DOC"] = False
        cmake.definitions["USE_OWN_EIGEN3"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "aruco")
        self.cpp_info.includedirs.append(os.path.join("include", "aruco"))
        self.cpp_info.libs = tools.collect_libs(self)
