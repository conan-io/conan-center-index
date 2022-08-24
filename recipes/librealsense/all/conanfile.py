from conan import ConanFile, tools
from conans import CMake
import os
import urllib


class LibrealsenseConan(ConanFile):
    name = "librealsense"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/IntelRealSense/librealsense"
    description = "Intel(R) RealSense(tm) Cross Platform API for accessing Intel RealSense cameras."
    topics = ("usb", "camera")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False],
        "rsusb_backend": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": True,
        "rsusb_backend": True, # TODO: change to False when CI gets MSVC ATL support
    }
    short_paths = True
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
        else:
            del self.options.rsusb_backend

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libusb/1.0.24")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

    def source(self):
        sources = self.conan_data["sources"][self.version]
        tools.files.get(self, **sources["source"], strip_root=True, destination=self._source_subfolder)
        for firmware in sources["firmware"]:
            filename = os.path.basename(urllib.parse.urlparse(firmware["url"]).path)
            tools.files.download(self, filename=filename, **firmware)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["CHECK_FOR_UPDATES"] = False
        self._cmake.definitions["BUILD_WITH_STATIC_CRT"] = False
        self._cmake.definitions["BUILD_EASYLOGGINGPP"] = False
        self._cmake.definitions["BUILD_TOOLS"] = self.options.tools
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_GLSL_EXTENSIONS"] = False
        self._cmake.definitions["BUILD_GRAPHICAL_EXAMPLES"] = False
        self._cmake.definitions["BUILD_INTERNAL_UNIT_TESTS"] = False
        self._cmake.definitions["BUILD_NETWORK_DEVICE"] = False
        self._cmake.definitions["BUILD_UNIT_TESTS"] = False
        self._cmake.definitions["BUILD_WITH_CUDA"] = False
        self._cmake.definitions["BUILD_WITH_OPENMP"] = False
        self._cmake.definitions["BUILD_WITH_TM2"] = True
        self._cmake.definitions["BUILD_PYTHON_BINDINGS"] = False
        self._cmake.definitions["BUILD_PYTHON_DOCS"] = False
        self._cmake.definitions["BUILD_NODEJS_BINDINGS"] = False
        self._cmake.definitions["BUILD_CV_EXAMPLES"] = False
        self._cmake.definitions["BUILD_DLIB_EXAMPLES"] = False
        self._cmake.definitions["BUILD_OPENVINO_EXAMPLES"] = False
        self._cmake.definitions["BUILD_OPEN3D_EXAMPLES"] = False
        self._cmake.definitions["BUILD_MATLAB_BINDINGS"] = False
        self._cmake.definitions["BUILD_PCL_EXAMPLES"] = False
        self._cmake.definitions["BUILD_UNITY_BINDINGS"] = False
        self._cmake.definitions["BUILD_CSHARP_BINDINGS"] = False
        self._cmake.definitions["BUILD_OPENNI2_BINDINGS"] = False
        self._cmake.definitions["BUILD_CV_KINFU_EXAMPLE"] = False
        if self.settings.os == "Windows":
            self._cmake.definitions["FORCE_RSUSB_BACKEND"] = self.options.rsusb_backend

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        if self.options.shared:
            postfix = "d" if self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug" else ""
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "libfw{}.*".format(postfix))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "librealsense-file{}.*".format(postfix))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        postfix = "d" if self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug" else ""

        self.cpp_info.names["cmake_find_package"] = "realsense2"
        self.cpp_info.names["cmake_find_package_multi"] = "realsense2"

        if not self.options.shared:
            self.cpp_info.components["fw"].libs = ["fw" + postfix]
            self.cpp_info.components["file"].libs = ["realsense-file" + postfix]

        self.cpp_info.components["realsense2"].libs = ["realsense2" + postfix]
        self.cpp_info.components["realsense2"].requires = ["libusb::libusb"]
        if not self.options.shared:
            self.cpp_info.components["realsense2"].requires.extend(["file", "fw"])
        self.cpp_info.components["realsense2"].names["pkg_config"] = "realsense2"
        if self.settings.os == "Linux":
            self.cpp_info.components["realsense2"].system_libs.extend(["m", "pthread", "udev"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["realsense2"].system_libs.extend([
                "cfgmgr32", "setupapi",
                "sensorsapi", "PortableDeviceGuids",
                "winusb",
                "shlwapi", "mf", "mfplat", "mfreadwrite", "mfuuid"
            ])
