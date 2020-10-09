from conans import ConanFile, CMake, tools
import os
import shutil


class mFASTConan(ConanFile):
    name = "mfast"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://objectcomputing.com/"
    description = "mFAST is a high performance C++ encoding/decoding library for FAST (FIX Adapted for STreaming)"\
                  " protocol"
    topics = ("conan", "mFAST", "FAST", "FIX", "Fix Adapted for STreaming", "Financial Information Exchange",
              "libraries", "cpp")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False}
    requires = ["boost/1.73.0", "tinyxml2/8.0.0"]
    generators = "cmake"
    exports_sources = "patches/**"
    short_paths = True
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("mFAST-" + self.version, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build(self):
        patches = self.conan_data["patches"][self.version]
        for patch in patches:
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("licence.txt", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Windows":
            shutil.move(os.path.join(self.package_folder, "CMake"),
                        os.path.join(self.package_folder, "lib", "cmake", "mFAST"))
        os.rename(os.path.join(self.package_folder, "lib", "cmake", "mFAST", "mFASTConfig.cmake"),
                  os.path.join(self.package_folder, "lib", "cmake", "mFAST", "mFASTTools.cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.builddirs = [os.path.join("lib", "cmake", "mFAST")]
        self.cpp_info.build_modules = [os.path.join("lib", "cmake", "mFAST", "mFASTTools.cmake")]
