import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import get, copy, rmdir
from conan.tools.system import PyEnv


required_conan_version = ">=2.23"

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
    no_copy_source = True

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("boost/[>=1.83.0 <1.90.0]")

    def validate(self):
        check_min_cppstd(self, 17)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        pyenv = PyEnv(self)
        pyenv.install(["Mako~=1.3"])
        pyenv.generate()

        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["PYTHON_EXECUTABLE"] = pyenv.env_exe
        tc.cache_variables["ENABLE_PYTHON_API"] = False
        tc.cache_variables["ENABLE_EXAMPLES"] = False
        tc.cache_variables["ENABLE_TESTS"] = False
        tc.cache_variables["ENABLE_B100"] = False
        tc.cache_variables["ENABLE_USRP1"] = False
        tc.cache_variables["ENABLE_X300"] = False
        tc.cache_variables["ENABLE_MPMD"] = False
        tc.cache_variables["ENABLE_OCTOCLOCK"] = False
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
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "uhd")
        self.cpp_info.set_property("cmake_target_name", "uhd::uhd")
        self.cpp_info.libs = ["uhd"]
        self.cpp_info.includedirs = ['include']
        self.cpp_info.libdirs = ['lib']
        self.cpp_info.bindirs = ['bin']

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")

        lib_path = os.path.join(self.package_folder, "lib")
        self.output.info(f"Appending LD_LIBRARY_PATH environment variable: {lib_path}")
