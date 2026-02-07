from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get
from conan.tools.files import copy
import os

required_conan_version = ">=2.0.0"


class ccronexprConan(ConanFile):
    name = "ccronexpr"
    license = "Apache-2.0"
    homepage = "https://github.com/exander77/supertinycron"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Cron expression parsing in ANSI C"
    topics = ("lib-static", "C", "cron", "cronexpr")
    
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_local_time": [True, False],
        "disable_years": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_local_time": False,
        "disable_years": False,
    }
    
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")
        
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CRON_COMPILE_AS_CXX"] = True
        tc.variables["CRON_DISABLE_TESTING"] = True
        tc.variables["CRON_USE_LOCAL_TIME"] = self.options.use_local_time
        if self.options.disable_years:
            tc.preprocessor_definitions["CRON_DISABLE_YEARS"] = None
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "ccronexpr.h", self.source_folder, os.path.join(self.package_folder, "include"), keep_path=False)
        for pattern in ["*.a", "*.so*", "*.dylib*", "*.lib"]:
            copy(self, pattern, dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, "*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["ccronexpr"]
        if self.options.disable_years:
            self.cpp_info.defines.append("CRON_DISABLE_YEARS")
