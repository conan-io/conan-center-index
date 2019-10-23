from conans import ConanFile, CMake, tools
import os
import glob


class OpenEXRConan(ConanFile):
    name = "openexr"
    description = "OpenEXR is a high dynamic-range (HDR) image file format developed by Industrial Light & " \
                  "Magic for use in computer imaging applications."
    license = "BSD"
    homepage = "https://github.com/openexr/openexr"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "namespace_versioning": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "namespace_versioning=True", "fPIC=True"
    generators = "cmake"
    exports_sources = ["IlmImf__ImfSystemSpecific.cpp.patch"]

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def requirements(self):
        self.requires('zlib/1.2.11')

    def configure(self):
        if "fPIC" in self.options.fields and self.options.shared:
            self.options.fPIC = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        tools.replace_in_file(os.path.join('openexr-{}'.format(self.version), 'CMakeLists.txt'),
                              'project(OpenEXR VERSION ${OPENEXR_VERSION})',
                              """project(OpenEXR VERSION ${OPENEXR_VERSION})
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

set(OPENEXR_PACKAGE_PREFIX ${CMAKE_INSTALL_PREFIX})

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
""")
        for p in self.conan_data["patches"][self.version]:
            tools.patch(**p)

    def build(self):
        # parallel builds are disabled due to the random issue: 'toFloat.h': No such file or directory
        cmake = CMake(self, parallel=self.settings.os != 'Windows')
        cmake.definitions["OPENEXR_BUILD_PYTHON_LIBS"] = False
        cmake.definitions["OPENEXR_BUILD_SHARED"] = self.options.shared
        cmake.definitions["OPENEXR_BUILD_STATIC"] = not bool(self.options.shared)
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

        if self.settings.os != "Windows":
            self.cpp_info.cppflags = ["-pthread"]
