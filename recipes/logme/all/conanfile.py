from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, rmdir
import os


class LogmeConan(ConanFile):
    name = "logme"
    package_type = "library"

    license = "Apache-2.0"
    url = "https://github.com/efmsoft/logme"
    homepage = "https://github.com/efmsoft/logme"
    description = "Lightweight cross-platform C/C++ logging framework."
    topics = ("logging", "log", "logger", "console", "file")

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_jsoncpp": [True, False],
        "std_format": ["AUTO", "ON", "OFF"],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jsoncpp": False,
        "std_format": "AUTO",
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        check_min_cppstd(self, 20)

    def requirements(self):
        if self.options.with_jsoncpp:
            self.requires("jsoncpp/1.9.6")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.variables["LOGME_BUILD_EXAMPLES"] = False
        tc.variables["LOGME_BUILD_TESTS"] = False
        tc.variables["LOGME_BUILD_TOOLS"] = False
        tc.variables["LOGME_ENABLE_INSTALL"] = True

        if bool(self.options.shared):
            tc.variables["LOGME_BUILD_STATIC"] = False
            tc.variables["LOGME_BUILD_DYNAMIC"] = True
        else:
            tc.variables["LOGME_BUILD_STATIC"] = True
            tc.variables["LOGME_BUILD_DYNAMIC"] = False

        tc.variables["USE_JSONCPP"] = bool(self.options.with_jsoncpp)
        tc.variables["LOGME_STD_FORMAT"] = str(self.options.std_format)

        if self.settings.os != "Windows":
            tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = bool(self.options.get_safe("fPIC"))

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "share", "doc"))
        rmdir(self, os.path.join(self.package_folder, "share", "man"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "logme")
        self.cpp_info.set_property("cmake_target_name", "logme::logme")

        if bool(self.options.shared):
            self.cpp_info.libs = ["logmed"]
        else:
            self.cpp_info.libs = ["logme"]

        if self.options.with_jsoncpp:
            self.cpp_info.defines.append("USE_JSONCPP")
