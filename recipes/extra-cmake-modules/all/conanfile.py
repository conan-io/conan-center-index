import os
#from conans import ConanFile, CMake, tools
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import get

class ExtracmakemodulesConan(ConanFile):
    name = "extra-cmake-modules"
    license = ("MIT", "BSD-2-Clause", "BSD-3-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://api.kde.org/ecm/"
    topics = ("conan", "cmake", "toolchain", "build-settings")
    description = "KDE's CMake modules"
    no_copy_source = False
    package_type = "build-scripts"
    settings = "build_type"
    

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder)


    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_HTML_DOCS"] = False
        tc.cache_variables["BUILD_QTHELP_DOCS"] = False
        tc.cache_variables["BUILD_MAN_DOCS"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.generate()


    def build(self):
        cm_folder = "{}-{}".format(self.name, self.version)
        cmake = CMake(self)
        cmake.configure(build_script_folder=cm_folder)

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_id(self):
        self.info.settings.clear()
        
 
    def package_old(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("testhelper.h", src=os.path.join(self.source_folder, self._source_subfolder, "tests/ECMAddTests"), dst="res/tests")
        self.copy("*", src=os.path.join(self.source_folder, self._source_subfolder, "LICENSES"), dst="licenses")

    def package_info(self):
        self.cpp_info.resdirs = ["res"]
        self.cpp_info.builddirs = ["res/ECM/cmake", "res/ECM/kde-modules", "res/ECM/modules", "res/ECM/test-modules", "res/ECM/toolchain"]

#    def package_id(self):
#        self.info.header_only()

