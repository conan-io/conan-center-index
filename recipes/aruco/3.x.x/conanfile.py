from conans import ConanFile, tools, CMake
import os


class LibnameConan(ConanFile):
    name = "aruco"
    description = "Augmented reality library based on OpenCV "
    topics = ("conan", "aruco", "augmented reality")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.uco.es/investiga/grupos/ava/node/26"
    license = "GPL-3.0-only"
    no_copy_source = True
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
    _cmake = None

    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [False, True], "fPIC": [False, True]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        # self.requires('opencv/4.2.0@conan/stable')
        self.requires('opencv/2.4.13.7@')
        self.requires('eigen/3.3.7@')
        self.requires('zlib/1.2.11@')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  filename='aruco.zip')
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = "OFF"
        self._cmake.definitions["BUILD_GLSAMPLES"] = "OFF"
        self._cmake.definitions["BUILD_UTILS"] = "OFF"
        self._cmake.definitions["BUILD_DEBPACKAGE"] = "OFF"
        self._cmake.definitions["USE_OWN_EIGEN"] = "OFF"
        self._cmake.configure(
            build_folder=self._build_subfolder
        )
        return self._cmake

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = ['include', 'include/aruco']
        self.cpp_info.libs = tools.collect_libs(self)
