import os
import urllib

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, download, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.0"


class LibrealsenseConan(ConanFile):
    name = "librealsense"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/IntelRealSense/librealsense"
    description = "Intel(R) RealSense(tm) Cross Platform API for accessing Intel RealSense cameras."
    topics = ("usb", "camera")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.rsusb_backend

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libusb/1.0.26")
        if Version(self.version) >= "2.50.0":
            self.requires("libudev/system")

    def validate(self):
        check_min_cppstd(self, 14)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        sources = self.conan_data["sources"][self.version]
        get(self, **sources["source"], strip_root=True)
        for firmware in sources["firmware"]:
            filename = os.path.basename(urllib.parse.urlparse(firmware["url"]).path)
            download(self, filename=filename, **firmware)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CHECK_FOR_UPDATES"] = False
        tc.variables["BUILD_WITH_STATIC_CRT"] = False
        tc.variables["BUILD_EASYLOGGINGPP"] = False
        tc.variables["BUILD_TOOLS"] = self.options.tools
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_GLSL_EXTENSIONS"] = False
        tc.variables["BUILD_GRAPHICAL_EXAMPLES"] = False
        tc.variables["BUILD_INTERNAL_UNIT_TESTS"] = False
        tc.variables["BUILD_NETWORK_DEVICE"] = False
        tc.variables["BUILD_UNIT_TESTS"] = False
        tc.variables["BUILD_WITH_CUDA"] = False
        tc.variables["BUILD_WITH_OPENMP"] = False
        tc.variables["BUILD_WITH_TM2"] = True
        tc.variables["BUILD_PYTHON_BINDINGS"] = False
        tc.variables["BUILD_PYTHON_DOCS"] = False
        tc.variables["BUILD_NODEJS_BINDINGS"] = False
        tc.variables["BUILD_CV_EXAMPLES"] = False
        tc.variables["BUILD_DLIB_EXAMPLES"] = False
        tc.variables["BUILD_OPENVINO_EXAMPLES"] = False
        tc.variables["BUILD_OPEN3D_EXAMPLES"] = False
        tc.variables["BUILD_MATLAB_BINDINGS"] = False
        tc.variables["BUILD_PCL_EXAMPLES"] = False
        tc.variables["BUILD_UNITY_BINDINGS"] = False
        tc.variables["BUILD_CSHARP_BINDINGS"] = False
        tc.variables["BUILD_OPENNI2_BINDINGS"] = False
        tc.variables["BUILD_CV_KINFU_EXAMPLE"] = False
        if self.settings.os == "Windows":
            tc.variables["FORCE_RSUSB_BACKEND"] = self.options.rsusb_backend
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if self.options.shared:
            postfix = "d" if is_msvc(self) and self.settings.build_type == "Debug" else ""
            rm(self, f"libfw{postfix}.*", os.path.join(self.package_folder, "lib"))
            rm(self, f"librealsense-file{postfix}.*", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "realsense2")

        postfix = "d" if is_msvc(self) and self.settings.build_type == "Debug" else ""
        if not self.options.shared:
            self.cpp_info.components["fw"].set_property("cmake_target_name", "realsense2::fw")
            self.cpp_info.components["fw"].libs = [f"fw{postfix}"]
            self.cpp_info.components["realsense-file"].set_property("cmake_target_name", "realsense2::realsense-file")
            self.cpp_info.components["realsense-file"].libs = [f"realsense-file{postfix}"]

        self.cpp_info.components["realsense2"].set_property("cmake_target_name", "realsense2::realsense2")
        self.cpp_info.components["realsense2"].set_property("pkg_config_name", "realsense2")
        self.cpp_info.components["realsense2"].libs = [f"realsense2{postfix}"]
        if not self.options.shared:
            self.cpp_info.components["realsense2"].requires.extend(["realsense-file", "fw"])
        self.cpp_info.components["realsense2"].requires = ["libusb::libusb"]
        if Version(self.version) >= "2.50.0":
            self.cpp_info.components["realsense2"].requires.append("libudev::libudev")
        if self.settings.os == "Linux":
            self.cpp_info.components["realsense2"].system_libs.extend(["m", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["realsense2"].system_libs.extend([
                "cfgmgr32", "setupapi",
                "sensorsapi", "portabledeviceguids",
                "winusb",
                "shlwapi", "mf", "mfplat", "mfreadwrite", "mfuuid"
            ])
