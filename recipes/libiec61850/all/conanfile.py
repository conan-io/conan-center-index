import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, replace_in_file, rmdir, rm
from conan.tools.scm import Version

required_conan_version = ">=2.1"

class Libiec61850Conan(ConanFile):
    name = "libiec61850"
    description = "An open-source library for the IEC 61850 protocols."
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libiec61850.com/libiec61850"
    topics = ("iec61850", "mms", "goose", "sampled values")

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

    languages = ["C"]
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_TESTS"] = False
        tc.cache_variables["FIND_PACKAGE_DISABLE_Doxygen"] = True
        tc.generate()

    def build(self):
        target_type = "-shared" if self.options.get_safe("shared") else ""
        replace_in_file(self, os.path.join(self.source_folder, "hal", "CMakeLists.txt"), 
                       "install (TARGETS hal hal-shared", f"install (TARGETS hal{target_type}")
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"), 
                       "install (TARGETS iec61850 iec61850-shared", f"install (TARGETS iec61850{target_type}")
        cmake = CMake(self)
        cmake.configure()
        target = "iec61850-shared" if self.options.get_safe("shared") else "iec61850"
        cmake.build(target=target)

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
            rm(self, pattern=dll_pattern_to_remove, folder=os.path.join(self.package_folder, "bin"), 
               recursive=True)

        if Version(self.version) == "1.6.0":
            # https://github.com/mz-automation/libiec61850/commit/a133aa8d573d63555899580869643590db9a7d85
            copy(self, "tls_ciphers.h", os.path.join(self.source_folder, "hal", "inc"),
                                        os.path.join(self.package_folder, "include", "libiec61850"))

    def package_info(self):
        self.cpp_info.components["iec61850"].libs = ["iec61850"]
        self.cpp_info.components["iec61850"].set_property("cmake_target_name", "iec61850")
        self.cpp_info.components["hal"].libs = ["hal-shared"] if self.options.get_safe("shared") else ["hal"]
        self.cpp_info.components["iec61850"].requires=["hal"]
        self.cpp_info.components["iec61850"].set_property("pkg_config_name", "libiec61850")
        if self.settings.os in ["Linux"]:
            self.cpp_info.components["iec61850"].system_libs.append("pthread")
            self.cpp_info.components["iec61850"].system_libs.append("rt")
