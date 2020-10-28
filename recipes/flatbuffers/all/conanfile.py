import glob
import os
import shutil
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.28.0"

class FlatbuffersConan(ConanFile):
    name = "flatbuffers"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://google.github.io/flatbuffers"
    topics = ("conan", "flatbuffers", "serialization", "rpc", "json-parser")
    description = "Memory Efficient Serialization Library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "header_only": [True, False], "flatc": [True, False], "flatbuffers": [True, False], "autodetect": [True, False] }
    default_options = {"shared": False, "fPIC": True, "header_only": False, "flatc": True, "flatbuffers": True, "autodetect": True}
    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            del self.options.fPIC
            del self.options.shared
        elif self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.options.autodetect:
            settings_target = getattr(self, 'settings_target', None)
            self.options.flatc = settings_target is not None
            self.options.flatbuffers = settings_target is None

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FLATBUFFERS_BUILD_TESTS"] = False
        self._cmake.definitions["FLATBUFFERS_BUILD_SHAREDLIB"] = self.options.flatbuffers and self.options.shared
        self._cmake.definitions["FLATBUFFERS_BUILD_FLATLIB"] = self.options.flatbuffers and not self.options.shared
        self._cmake.definitions["FLATBUFFERS_BUILD_FLATC"] = self.options.flatc
        self._cmake.definitions["FLATBUFFERS_BUILD_FLATHASH"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        if not self.options.header_only or self.options.flatc:
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        
        if ( self.options.flatbuffers and not self.options.header_only ) or self.options.flatc:
            cmake = self._configure_cmake()
            cmake.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        
        if self.options.flatbuffers:
            self.copy(pattern="BuildFlatBuffers.cmake", dst="bin/cmake", src=os.path.join(self._source_subfolder,"CMake"))
            
        if self.options.flatbuffers and self.options.header_only:
            header_dir = os.path.join(self._source_subfolder, "include", "flatbuffers")
            dst_dir = os.path.join("include", "flatbuffers")
            self.copy("*.h", dst=dst_dir, src=header_dir)
            
        if self.options.flatbuffers and not self.options.header_only:
            if self.settings.os == "Windows" and self.options.shared:
                tools.mkdir(os.path.join(self.package_folder, "bin"))
                for dll_path in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
                    shutil.move(dll_path, os.path.join(self.package_folder, "bin", os.path.basename(dll_path)))
        
        if not self.options.flatbuffers and not self.options.header_only and self.options.flatc:
            tools.rmdir(os.path.join(self.package_folder, "include"))

    def package_info(self):  
        if self.options.flatbuffers:
            self.cpp_info.filenames["cmake_find_package"] = "Flatbuffers"
            self.cpp_info.filenames["cmake_find_package_multi"] = "Flatbuffers"
            self.cpp_info.names["cmake_find_package"] = "flatbuffers"
            self.cpp_info.names["cmake_find_package_multi"] = "flatbuffers"           
        if self.options.flatbuffers and not self.options.header_only:
            cmake_target = "flatbuffers_shared" if self.options.shared else "flatbuffers"
            self.cpp_info.components["libflatbuffers"].names["cmake_find_package"] = cmake_target
            self.cpp_info.components["libflatbuffers"].names["cmake_find_package_multi"] = cmake_target
            self.cpp_info.components["libflatbuffers"].libs = tools.collect_libs(self)
            self.cpp_info.components["libflatbuffers"].builddirs.append("bin/cmake")
            self.cpp_info.components["libflatbuffers"].build_modules.append("bin/cmake/BuildFlatBuffers.cmake")
            if self.settings.os == "Linux":
                self.cpp_info.components["libflatbuffers"].system_libs.append("m")
        if self.options.flatbuffers and self.options.header_only:
            self.cpp_info.builddirs.append("bin/cmake")
            self.cpp_info.build_modules.append("bin/cmake/BuildFlatBuffers.cmake")  
        if self.options.flatc:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info('Appending PATH environment variable: %s' % bin_path)
            self.env_info.PATH.append(bin_path)
