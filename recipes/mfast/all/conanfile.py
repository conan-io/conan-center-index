from conans import ConanFile, CMake, tools
import glob
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
    requires = ["boost/1.74.0", "tinyxml2/8.0.0"]
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    short_paths = True
    _cmake = None

    @property
    def _old_mfast_config_dir(self):
        return os.path.join("CMake") if self.settings.os == "Windows" else os.path.join("lib", "cmake", "mFAST")

    @property
    def _new_mfast_config_dir(self):
        return os.path.join("res") if self.settings.os == "Windows" else os.path.join("lib", "cmake", "mFAST")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_TESTS"] = False
            self._cmake.definitions["BUILD_EXAMPLES"] = False
            self._cmake.definitions["BUILD_PACKAGES"] = False
            if self.version != "1.2.1":
                if not self.settings.compiler.cppstd:
                    self._cmake.definitions["CMAKE_CXX_STANDARD"] = 14
                else:
                    tools.check_min_cppstd(self, 14)
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("mFAST-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

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
        # This makes hook error go away
        shutil.move(
            os.path.join(self.package_folder, self._old_mfast_config_dir),
            os.path.join(self.package_folder, self._new_mfast_config_dir)
        )
        os.rename(
            os.path.join(self.package_folder, self._new_mfast_config_dir, "mFASTConfig.cmake"),
            os.path.join(self.package_folder, self._new_mfast_config_dir, "mFASTTools.cmake")
        )
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.builddirs = [self._new_mfast_config_dir]
        self.cpp_info.build_modules = [os.path.join(self._new_mfast_config_dir, "mFASTTools.cmake")]
