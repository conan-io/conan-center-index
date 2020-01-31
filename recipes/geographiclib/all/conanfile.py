from conans import ConanFile, CMake, tools
import os

class GeographiclibConan(ConanFile):
    name = "geographiclib"
    description = "Convert geographic units and solve geodesic problems"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://geographiclib.sourceforge.io"
    license = "MIT"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    def config_options(self):
        if self.settings.os == 'Windows':
            self.options.remove("fPIC")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "GeographicLib-" + self.version
        os.rename(extracted_dir, self._source_subfolder)


    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions['GEOGRAPHICLIB_LIB_TYPE'] = 'SHARED' if self.options.shared else 'STATIC'
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        # it does not work on Windows but is not needed
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "add_subdirectory (js)", "")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        for folder in ["share", os.path.join("lib", "python"), os.path.join("lib", "pkgconfig"), os.path.join("lib", "cmake"), "sbin", "python", "matlab", "doc", "cmake"]:
            tools.rmdir(os.path.join(os.path.join(self.package_folder, folder)))
        if self.settings.os == "Linux":
            tools.rmdir(os.path.join(os.path.join(self.package_folder, "bin")))
        elif self.settings.os == "Windows":
            for item in os.listdir(os.path.join(os.path.join(self.package_folder, "bin"))):
                if not item.startswith("Geographic") or item.endswith(".pdb"):
                    os.remove(os.path.join(self.package_folder, "bin", item))


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include", os.path.join("include","GeographicLib")]
        self.cpp_info.defines.append('GEOGRAPHICLIB_SHARED_LIB={}'.format("1" if self.options.shared else "0"))
