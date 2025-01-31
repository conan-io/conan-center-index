from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import copy
from conan.errors import ConanException
import os, shutil

class StdxConan(ConanFile):
    name = "stdx"
    version = "0.1.4"
    license = "MIT"
    author = "Yashar A.Rezaei"
    url = "https://github.com/yrezaei/stdx"
    description = "Collection of C++ modules"
    topics = ("logger", "flag", "utilities")
    exports = "conanfile.py"
    exports_sources = "*"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "local_dev": [True, False],
        "enable_flag": [True, False],
        "enable_logger": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "local_dev": False,
        "enable_flag": True,
        "enable_logger": True,
    }
    dev_mode = False

    def configure(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        self.dev_mode = self.options.local_dev

    def layout(self):
        pass  # Layout can be configured if needed

    def source(self):
        # Check the local_dev option
        if self.dev_mode:
            self.output.info("Local development mode detected. Skipping download.")
            # Ensure that source files exist in the current folder
            if not os.path.exists(self.source_folder):
                raise ConanException("Local source folder not found for development mode.")
            return
        self.output.info("Downloading source code...")
        self.run("curl -L -o stdx-v{}.tar.gz https://github.com/yRezaei/stdx/archive/refs/tags/v{}.tar.gz".format(self.version, self.version))
        self.run("tar -xzf stdx-v{}.tar.gz".format(self.version))
        # Use shutil for moving files cross-platform
        extracted_folder = "stdx-{}".format(self.version)
        for item in os.listdir(extracted_folder):
            s = os.path.join(extracted_folder, item)
            d = os.path.join(self.source_folder, item)
            if os.path.isdir(s):
                shutil.move(s, d)
            else:
                shutil.move(s, d)
        # Remove the extracted folder after moving its contents
        shutil.rmtree(extracted_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_BUILD_TYPE"] = str(self.settings.build_type)

        # If user says -o stdx:shared=True, then set BUILD_SHARED_LIBS=ON
        tc.cache_variables["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"

        # Pass module enable flags to CMake
        tc.cache_variables["STDX_ENABLE_FLAG"] = \
            "ON" if self.options.enable_flag else "OFF"
        tc.cache_variables["STDX_ENABLE_LOGGER"] = \
            "ON" if self.options.enable_logger else "OFF"

        tc.generate()

        # Generate CMakeDeps for each module
        cd = CMakeDeps(self)
        cd.generate()
        cd.configuration = []

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        if self.options.enable_logger:
            self.cpp_info.libs.append("logger")
