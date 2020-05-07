import os
from conans import ConanFile, CMake, tools


class SundialsTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    short_paths = True
    
    def build(self):
        cmake = CMake(self)
        if self.options["sundials"].build_cvode:
            cmake.definitions["WITH_CVODE"] = "TRUE"
        if self.options["sundials"].build_cvodes:
            cmake.definitions["WITH_CVODES"] = "TRUE"
        if self.options["sundials"].build_arkode:
            cmake.definitions["WITH_ARKODE"] = "TRUE"
        if self.options["sundials"].build_ida:
            cmake.definitions["WITH_IDA"] = "TRUE"
        if self.options["sundials"].build_idas:
            cmake.definitions["WITH_IDAS"] = "TRUE"
        if self.options["sundials"].build_kinsol:
            cmake.definitions["WITH_KINSOL"] = "TRUE"
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            if self.options["sundials"].build_cvode:
                self.run(os.path.join("bin", "test_package_cvode"),
                         run_environment=True)
            if self.options["sundials"].build_cvodes:
                self.run(os.path.join("bin", "test_package_cvodes"),
                         run_environment=True)
            if self.options["sundials"].build_arkode:
                self.run(os.path.join("bin", "test_package_arkode"),
                         run_environment=True)
            if self.options["sundials"].build_ida:
                self.run(os.path.join("bin", "test_package_ida"),
                         run_environment=True)
            if self.options["sundials"].build_idas:
                self.run(os.path.join("bin", "test_package_idas"),
                         run_environment=True)
            if self.options["sundials"].build_kinsol:
                self.run(os.path.join("bin", "test_package_kinsol"),
                         run_environment=True)
