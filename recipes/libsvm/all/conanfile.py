from conans import ConanFile, tools, CMake
import os
import shutil

class libsvmConan(ConanFile):
    name = "libsvm"
    description = "Libsvm is a simple, easy-to-use, and efficient software for SVM classification and regression"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.csie.ntu.edu.tw/~cjlin/libsvm/"
    license = "BSD-3-Clause"
    topics = ("conan", "svm", "vector")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        #Use custom CMakeLists.txt
        shutil.copy(src=os.path.join(self.source_folder, "CMakeLists.txt"), dst=os.path.join(self.source_folder,self._source_subfolder))
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYRIGHT", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "LibSVM"
        self.cpp_info.names["cmake_find_package_multi"] = "LibSVM"
