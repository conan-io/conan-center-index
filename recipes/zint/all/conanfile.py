from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"

class ZintConan(ConanFile):
    name = "zint"
    description = "Zint Barcode Generator"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/p/zint/code"
    license = "GPL-3.0"
    topics = ("conan", "barcode", "qt")
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package_multi", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False],
        "with_qt" : [True, False],
        "with_libpng" : [True, False]
    }
    default_options = {
        "shared": False, 
        "fPIC": True,
        "with_qt": False,
        "with_libpng": True
    }

    _cmake = None
   
    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):

        self.requires("zlib/1.2.11")
        if self.options.with_libpng:
            self.requires("libpng/1.6.37")
        if self.options.with_qt:
            self.requires("qt/5.15.2")
    
    def validate(self):
    
        if self.options.with_qt:
            if not all((self.options["qt"].widgets, self.options["qt"].gui, self.options["qt"].qttools)):
                raise ConanInvalidConfiguration(f"{self.name} needs qt:{{widgets,gui,qttools}}=True")


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)
        


    def _configure_cmake(self):
        if self._cmake:
            return self._cmake   
        self._cmake = CMake(self)
        self._cmake.definitions["ZINT_USE_QT"] = self.options.with_qt
        self._cmake.definitions["ZINT_USE_PNG"] = self.options.with_libpng
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
 
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.components["libzint"].libs = ["zint"]
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
                self.cpp_info.components["libzint"].libs.append("zint_bundled_getopt")
        self.cpp_info.components["libzint"].names["cmake_find_package"] = "Zint"
        self.cpp_info.components["libzint"].names["cmake_find_package_multi"] = "Zint"
        self.cpp_info.components["libzint"].requires = ["zlib::zlib"]
        
        if self.options.with_libpng:
            self.cpp_info.components["libzint"].requires.append("libpng::libpng")
            
        if self.options.with_qt:
            self.cpp_info.components["libqzint"].libs = ["QZint"]
            self.cpp_info.components["libqzint"].names["cmake_find_package"] = "QZint"
            self.cpp_info.components["libqzint"].names["cmake_find_package_multi"] = "QZint"
            self.cpp_info.components["libqzint"].requires.extend([
                "libzint",
                "qt::gui", 
                "qt::widgets",
                "qt::qttools"
            ])
        if self.options.with_qt:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs = ["dwmapi", "uxtheme"]

        self.cpp_info.filenames["cmake_find_package"] = "Zint"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Zint"
