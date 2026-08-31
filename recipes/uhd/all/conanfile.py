import os
from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir, replace_in_file, rm
from conan.tools.system import PyEnv
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=2.26"


class UhdConan(ConanFile):
    name = "uhd"
    description = (
        "The USRP Hardware Driver (UHD) software for Ettus Research USRP "
        "software-defined radio devices."
    )
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/EttusResearch/uhd"
    topics = ("sdr", "usrp", "uhd", "radio", "driver")
    languages = "C", "C++"
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("boost/[>=1.83.0 <2]")
        self.requires("libusb/1.0.29")

    def validate(self):
        check_min_cppstd(self, 17)

        if self.settings.os == "Windows" and not self.options.shared:
            raise ConanInvalidConfiguration("There is a bug in Windows-Static: https://github.com/EttusResearch/uhd/issues/925")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "host", "CMakeLists.txt"), "add_subdirectory(docs)", "#add_subdirectory(docs)")
        replace_in_file(self, os.path.join(self.source_folder, "host", "CMakeLists.txt"), "set(CMAKE_CXX_STANDARD 20)", "")

    def generate(self):
        pyenv = PyEnv(self)
        pyenv.install(["Mako~=1.3"])
        pyenv.generate()

        deps = CMakeDeps(self)
        if Version(self.dependencies["boost"].ref.version) >= "1.89.0":
            deps.set_property("boost::headers", "cmake_target_aliases", ["Boost::system"])
        deps.set_property("libusb", "cmake_file_name", "LIBUSB")
        deps.set_property("libusb", "cmake_target_name", "LIBUSB::LIBUSB")
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.cache_variables["UHD_VERSION"] = str(self.version)
        tc.cache_variables["UHD_GIT_BRANCH_OVERRIDE"] = f"UHD-{self.version}"
        if is_apple_os(self):
            tc.cache_variables["CMAKE_INSTALL_NAME_DIR"] = "@rpath"
            tc.cache_variables["CMAKE_INSTALL_RPATH"] = ""
        tc.cache_variables["PYTHON_EXECUTABLE"] = pyenv.env_exe
        tc.cache_variables["ENABLE_PYTHON_API"] = False
        tc.cache_variables["ENABLE_EXAMPLES"] = False
        tc.cache_variables["ENABLE_TESTS"] = False
        tc.cache_variables["ENABLE_B100"] = True
        tc.cache_variables["ENABLE_B200"] = True
        tc.cache_variables["ENABLE_USRP1"] = True
        tc.cache_variables["ENABLE_USRP2"] = True
        tc.cache_variables["ENABLE_X300"] = True
        tc.cache_variables["ENABLE_MPMD"] = True
        tc.cache_variables["ENABLE_OCTOCLOCK"] = True
        tc.cache_variables["ENABLE_STATIC_LIBS"] = not self.options.shared
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="host")
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if not self.options.shared:
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dylib*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dll*", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "uhd")
        self.cpp_info.set_property("cmake_target_name", "uhd::uhd")
        self.cpp_info.libs = ["uhd"]

        bin_path = os.path.join(self.package_folder, "bin")

        lib_path = os.path.join(self.package_folder, "lib")
