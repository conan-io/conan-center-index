from conans import ConanFile, CMake, tools
import os
import glob


class OpenEXRConan(ConanFile):
    name = "openexr"
    description = "OpenEXR is a high dynamic-range (HDR) image file format developed by Industrial Light & " \
                  "Magic for use in computer imaging applications."
    license = "BSD-3-Clause"
    homepage = "https://github.com/openexr/openexr"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "namespace_versioning": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "namespace_versioning": True, "fPIC": True}
    generators = "cmake"
    exports_sources = ["patches/*.patch"]

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def requirements(self):
        self.requires('zlib/1.2.11')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        for p in self.conan_data["patches"][self.version]:
            tools.patch(**p)

    def build(self):
        # parallel builds are disabled due to the random issue: 'toFloat.h': No such file or directory
        cmake = CMake(self, parallel=self.settings.os != 'Windows')
        cmake.definitions["OPENEXR_BUILD_PYTHON_LIBS"] = False
        cmake.definitions["OPENEXR_BUILD_SHARED"] = self.options.shared
        cmake.definitions["OPENEXR_BUILD_STATIC"] = not self.options.shared
        cmake.definitions["OPENEXR_NAMESPACE_VERSIONING"] = self.options.namespace_versioning
        cmake.definitions["OPENEXR_ENABLE_TESTS"] = False
        cmake.definitions["OPENEXR_FORCE_CXX03"] = True
        cmake.definitions["OPENEXR_BUILD_UTILS"] = False
        cmake.definitions["ENABLE_TESTS"] = False
        cmake.definitions["OPENEXR_BUILD_TESTS"] = False

        cmake.configure(source_dir='openexr-{}'.format(self.version))
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        self.copy("license*", dst="licenses", src="openexr-%s/IlmBase" % self.version, ignore_case=True, keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        with tools.chdir(os.path.join(self.package_folder, "lib")):
            for filename in glob.glob("*.la"):
                os.unlink(filename)

    def package_info(self):
        parsed_version = self.version.split('.')
        version_suffix = "-%s_%s" % (parsed_version[0], parsed_version[1]) if self.options.namespace_versioning else ""
        if not self.options.shared:
            version_suffix += "_s"
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
            self.cpp_info.libs.append("pthread")
