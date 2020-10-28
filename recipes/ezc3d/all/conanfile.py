import os

from conans import ConanFile, CMake, tools

class Ezc3dConan(ConanFile):
    name = "ezc3d"
    description = "EZC3D is an easy to use reader, modifier and writer for C3D format files."
    license = "MIT"
    topics = ("conan", "ezc3d", "c3d")
    homepage = "https://github.com/pyomeca/ezc3d"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "ezc3d-Release_{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # don't force PIC
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")
        # fix install
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(${PROJECT_NAME}_LIB_FOLDER Lib)",
                              "set(${PROJECT_NAME}_LIB_FOLDER lib)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(${PROJECT_NAME}_LIB_FOLDER lib/${PROJECT_NAME})",
                              "set(${PROJECT_NAME}_LIB_FOLDER lib)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(${PROJECT_NAME}_BIN_FOLDER lib/${PROJECT_NAME})",
                              "set(${PROJECT_NAME}_BIN_FOLDER bin)")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_MATRIX_FAST_ACCESSOR"] = True
        self._cmake.definitions["BINDER_PYTHON3"] = False
        self._cmake.definitions["BINDER_MATLAB"] = False
        self._cmake.definitions["BUILD_EXAMPLE"] = False
        self._cmake.definitions["BUILD_DOC"] = False
        self._cmake.definitions["GET_OFFICIAL_DOCUMENTATION"] = False
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        # FIXME: remove namespace for imported target
        self.cpp_info.includedirs.append(os.path.join("include", "ezc3d"))
        lib_suffix = {"Debug": "_debug"}.get(str(self.settings.build_type), "")
        self.cpp_info.libs = ["ezc3d" + lib_suffix]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
