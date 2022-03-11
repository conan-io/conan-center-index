import glob
import os
import shutil
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class FlatbuffersConan(ConanFile):
    name = "flatbuffers"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://google.github.io/flatbuffers"
    topics = ("conan", "flatbuffers", "serialization", "rpc", "json-parser")
    description = "Memory Efficient Serialization Library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "header_only": [True, False],
               "flatc": [True, False],
               "flatbuffers": [True, False],
               "options_from_context": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True, "header_only": False,
                       "flatc": True,
                       "flatbuffers": True,
                       "options_from_context": True}
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"

    _cmake = None
    _header_only = False

    @property
    def _source_subfolder(self):
        return "source_subfolder"
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def configure(self):
        # Detect if host or build context
        if self.options.options_from_context:
            settings_target = getattr(self, 'settings_target', None)
            self.options.flatc = settings_target is not None
            self.options.flatbuffers = settings_target is None
        del self.options.options_from_context

        if not self.options.flatbuffers:
            del self.options.header_only
            self._header_only = False
        else:
            self._header_only = self.options.header_only

        if (self.options.shared and self.options.flatbuffers) or self._header_only or (not self.options.flatbuffers and self.options.flatc):
            del self.options.fPIC
            
        if self._header_only and not self.options.flatc:
            del self.options.shared

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        if self._header_only and not self.options.flatc:
            self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FLATBUFFERS_BUILD_TESTS"] = False
        self._cmake.definitions["FLATBUFFERS_BUILD_SHAREDLIB"] = self.options.flatbuffers and self.options.shared
        self._cmake.definitions["FLATBUFFERS_BUILD_FLATLIB"] = self.options.flatbuffers and not self.options.shared
        self._cmake.definitions["FLATBUFFERS_BUILD_FLATC"] = self.options.flatc
        self._cmake.definitions["FLATBUFFERS_BUILD_FLATHASH"] = False
        self._cmake.definitions["FLATBUFFERS_STATIC_FLATC"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        if (self.options.flatbuffers and not self._header_only) or self.options.flatc:
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)

        # Run cmake if there is anything to build
        if (self.options.flatbuffers and not self._header_only) or self.options.flatc:
            cmake = self._configure_cmake()
            cmake.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        if self.options.flatbuffers:
            self.copy(pattern="BuildFlatBuffers.cmake", dst="bin/cmake", src=os.path.join(self._source_subfolder, "CMake"))

            if self._header_only:
                header_dir = os.path.join(self._source_subfolder, "include", "flatbuffers")
                dst_dir = os.path.join("include", "flatbuffers")
                self.copy("*.h", dst=dst_dir, src=header_dir)

            if not self._header_only:
                if self.settings.os == "Windows" and self.options.shared:
                    tools.mkdir(os.path.join(self.package_folder, "bin"))
                    for dll_path in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
                        shutil.move(dll_path, os.path.join(self.package_folder, "bin", os.path.basename(dll_path)))
        elif self.options.flatc:
            tools.rmdir(os.path.join(self.package_folder, "include"))

    def package_info(self):
        if self.options.flatbuffers:
            self.cpp_info.filenames["cmake_find_package"] = "Flatbuffers"
            self.cpp_info.filenames["cmake_find_package_multi"] = "Flatbuffers"
            self.cpp_info.names["cmake_find_package"] = "flatbuffers"
            self.cpp_info.names["cmake_find_package_multi"] = "flatbuffers"
            self.cpp_info.names["pkg_config"] = "flatbuffers"
            if not self._header_only:
                cmake_target = "flatbuffers_shared" if self.options.shared else "flatbuffers"
                self.cpp_info.components["libflatbuffers"].names["cmake_find_package"] = cmake_target
                self.cpp_info.components["libflatbuffers"].names["cmake_find_package_multi"] = cmake_target
                self.cpp_info.components["libflatbuffers"].libs = tools.collect_libs(self)
                self.cpp_info.components["libflatbuffers"].builddirs.append("bin/cmake")
                self.cpp_info.components["libflatbuffers"].build_modules.append("bin/cmake/BuildFlatBuffers.cmake")
                if self.settings.os == "Linux":
                    self.cpp_info.components["libflatbuffers"].system_libs.append("m")
            else:
                self.cpp_info.builddirs.append("bin/cmake")
                self.cpp_info.build_modules.append("bin/cmake/BuildFlatBuffers.cmake")
        if self.options.flatc:
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bindir))
            self.env_info.PATH.append(bindir)
