from conans import ConanFile, CMake, tools
import os, shutil

class OpenEXRConan(ConanFile):
    name = "opencolorio"
    description = "A color management framework for visual effects and animation."
    license = "BSD-3-Clause"
    homepage = "https://opencolorio.org/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake", "cmake_find_package"
    exports_sources = ["patches/*"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def requirements(self):
        self.requires("lcms/2.11")
        self.requires("yaml-cpp/0.6.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("OpenColorIO-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)

        self._cmake.definitions["OCIO_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["OCIO_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["OCIO_BUILD_APPS"] = False
        self._cmake.definitions["OCIO_BUILD_DOCS"] = False
        self._cmake.definitions["OCIO_BUILD_TESTS"] = False
        self._cmake.definitions["OCIO_BUILD_PYGLUE"] = False
        self._cmake.definitions["USE_EXTERNAL_TINYXML"] = False
        self._cmake.definitions["USE_EXTERNAL_YAML"] = True
        self._cmake.definitions["USE_EXTERNAL_LCMS"] = True
        self._cmake.definitions["TINYXML_OBJECT_LIB_EMBEDDED"] = True
        self._cmake.definitions["YAML_CPP_VERSION"] = self.deps_cpp_info["yaml-cpp"].version
        
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()

        cm = self._configure_cmake()
        cm.build()

    def package(self):
        cm = self._configure_cmake()
        cm.install()

        if not self.options.shared:
            self.copy("*", src=os.path.join(self.package_folder, "lib", "static"), dst="lib")
            shutil.rmtree(path=os.path.join(self.package_folder, "lib", "static"))

        shutil.rmtree(path=os.path.join(self.package_folder, "cmake"))
        shutil.rmtree(path=os.path.join(self.package_folder, "lib", "pkgconfig"))
        shutil.rmtree(path=os.path.join(self.package_folder, "share"))
        os.remove(os.path.join(self.package_folder, "OpenColorIOConfig.cmake"))

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "OpenColorIO"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenColorIO"
        self.cpp_info.names["pkg_config"] = "OpenColorIO"

        self.cpp_info.libs = tools.collect_libs(self)

        if not self.options.shared:
            self.cpp_info.defines.append("OpenColorIO_STATIC")
