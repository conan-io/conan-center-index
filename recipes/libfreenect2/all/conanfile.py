from conans import ConanFile, CMake, tools
import os


class Libfreenect2Conan(ConanFile):
    name = "libfreenect2"
    license = ("Apache-2.0", "GPL-2.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/OpenKinect/libfreenect2"
    description = "Open source drivers for the Kinect for Windows v2 device."
    topics = ("usb", "camera", "kinect")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_opencl": [True, False],
        "with_opengl": [True, False],
        "with_vaapi": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_opencl": True,
        "with_opengl": True,
        "with_vaapi": True,
    }
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/*"]

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
        if self.settings.os != "Linux":
            del self.options.with_vaapi

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libusb/1.0.24")
        self.requires("libjpeg-turbo/2.1.1")
        if self.options.with_opencl:
            self.requires("opencl-headers/2021.04.29")
            self.requires("opencl-icd-loader/2021.04.29")
        if self.options.with_opengl:
            self.requires("opengl/system")
            self.requires("glfw/3.3.4")
        if self.options.get_safe("with_vaapi"):
            self.requires("vaapi/system")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_OPENNI2_DRIVER"] = False
        self._cmake.definitions["ENABLE_CXX11"] = True
        self._cmake.definitions["ENABLE_OPENCL"] = self.options.with_opencl
        self._cmake.definitions["ENABLE_CUDA"] = False # TODO: CUDA
        self._cmake.definitions["ENABLE_OPENGL"] = self.options.with_opengl
        self._cmake.definitions["ENABLE_VAAPI"] = self.options.get_safe("with_vaapi", False)
        self._cmake.definitions["ENABLE_TEGRAJPEG"] = False # TODO: TegraJPEG
        self._cmake.definitions["ENABLE_PROFILING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("APACHE20", src=self._source_subfolder, dst="licenses", keep_path=False)
        self.copy("GPL2", src=self._source_subfolder, dst="licenses", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "freenect2"
        self.cpp_info.names["cmake_find_package_multi"] = "freenect2"
        self.cpp_info.names["pkg_config"] = "freenect2"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["VideoToolbox", "CoreFoundation", "CoreMedia", "CoreVideo"])
