from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=1.53.0"


class LibfreenectConan(ConanFile):
    name = "libfreenect"
    license = ("Apache-2.0", "GPL-2.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/OpenKinect/libfreenect"
    description = "Drivers and libraries for the Xbox Kinect device."
    topics = ("usb", "camera", "kinect")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libusb/1.0.26")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_REDIST_PACKAGE"] = True
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_FAKENECT"] = False
        tc.variables["BUILD_C_SYNC"] = False
        tc.variables["BUILD_CPP"] = False
        tc.variables["BUILD_CV"] = False
        tc.variables["BUILD_AS3_SERVER"] = False
        tc.variables["BUILD_PYTHON"] = False
        tc.variables["BUILD_PYTHON2"] = False
        tc.variables["BUILD_PYTHON3"] = False
        tc.variables["BUILD_OPENNI2_DRIVER"] = False
        # Relocatable shared libs on macOS
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "APACHE20", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "GPL", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libfreenect")
        self.cpp_info.libs = ["freenect"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
