from conans import ConanFile, CMake, tools
import os
class OpenEXRConan(ConanFile):
    name = "openexr"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/openexr/openexr"
    topics = ("conan", "hdr", "image", "picture", "graphic")
    license = "BSD-3-Clause"
    description = "OpenEXR is a high dynamic-range (HDR) image file format for use in computer imaging applications"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "namespace_versioning": [True, False]}
    default_options = {"shared": False, "namespace_versioning": True, 'fPIC': True}
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/0001-find-zlib.patch"]
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "openexr-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def requirements(self):
        self.requires.add("zlib/1.2.11")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["OPENEXR_BUILD_PYTHON_LIBS"] = False
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["OPENEXR_VIEWERS_ENABLE"] = False
        cmake.definitions["OPENEXR_BUILD_SHARED"] = self.options.shared
        cmake.definitions["OPENEXR_BUILD_STATIC"] = not self.options.shared
        cmake.definitions["OPENEXR_NAMESPACE_VERSIONING"] = self.options.namespace_versioning
        cmake.definitions["OPENEXR_ENABLE_TESTS"] = False
        cmake.definitions["OPENEXR_FORCE_CXX03"] = True
        cmake.definitions["OPENEXR_BUILD_UTILS"] = False
        cmake.definitions["ENABLE_TESTS"] = False
        cmake.definitions["OPENEXR_BUILD_TESTS"] = False

        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        tools.patch(**self.conan_data["patches"][self.version])
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        parsed_version = self.version.split('.')
        version_suffix = "-%s_%s" % (parsed_version[0], parsed_version[1]) if self.options.namespace_versioning else ""
        #if not self.options.shared:
        #    version_suffix += "_s"
        if self.settings.compiler == 'Visual Studio' and self.settings.build_type == 'Debug':
            version_suffix += "_d"
        self.cpp_info.libs = ['IlmImf' + version_suffix,
                              'IlmImfUtil' + version_suffix,
                              'IlmThread' + version_suffix,
                              'Iex' + version_suffix,
                              'Half' + version_suffix]
        
        self.cpp_info.includedirs = [os.path.join('include', 'OpenEXR'), 'include']
        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("OPENEXR_DLL")

        if self.settings.os == "Linux":
            self.cpp_info.cppflags = ["pthread"]
