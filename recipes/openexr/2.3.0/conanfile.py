from conans import ConanFile, CMake, tools
import glob
import os


class OpenEXRConan(ConanFile):
    name = "openexr"
    version = "2.3.0"
    description = "OpenEXR is a high dynamic-range (HDR) image file format developed by Industrial Light & " \
                  "Magic for use in computer imaging applications."
    topics = ("conan", "openexr", "hdr", "image", "picture")
    license = "BSD-3-Clause"
    homepage = "https://github.com/openexr/openexr"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "namespace_versioning": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "namespace_versioning": True, "fPIC": True}
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/*.patch"]

    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def requirements(self):
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("openexr-{}".format(self.version), self._source_subfolder)
        for p in self.conan_data["patches"][self.version]:
            tools.patch(**p)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["OPENEXR_BUILD_PYTHON_LIBS"] = False
        cmake.definitions["BUILD_ILMBASE_STATIC"] = not self.options.shared
        cmake.definitions["OPENEXR_BUILD_SHARED"] = self.options.shared
        cmake.definitions["OPENEXR_BUILD_STATIC"] = not self.options.shared
        cmake.definitions["OPENEXR_NAMESPACE_VERSIONING"] = self.options.namespace_versioning
        cmake.definitions["OPENEXR_ENABLE_TESTS"] = False
        cmake.definitions["OPENEXR_FORCE_CXX03"] = False
        cmake.definitions["OPENEXR_BUILD_UTILS"] = False
        cmake.definitions["ENABLE_TESTS"] = False
        cmake.definitions["OPENEXR_BUILD_TESTS"] = False
        cmake.configure()
        return cmake

    def _patch_sources(self):
        # Fix dependency of IlmBase
        tools.replace_in_file(os.path.join(self._source_subfolder, "IlmBase", "Half", "CMakeLists.txt"),
                              "ADD_LIBRARY ( Half_static STATIC\n    half.cpp",
                              "ADD_LIBRARY ( Half_static STATIC\n    half.cpp \"${CMAKE_CURRENT_BINARY_DIR}/eLut.h\" \"${CMAKE_CURRENT_BINARY_DIR}/toFloat.h\"")
        tools.replace_in_file(os.path.join(self._source_subfolder, "IlmBase", "Half", "CMakeLists.txt"),
                              "ADD_LIBRARY ( Half SHARED\n    half.cpp",
                              "ADD_LIBRARY ( Half SHARED\n    half.cpp \"${CMAKE_CURRENT_BINARY_DIR}/eLut.h\" \"${CMAKE_CURRENT_BINARY_DIR}/toFloat.h\"")
        # Don't let the build script override static/shared of IlmBase
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(BUILD_ILMBASE_STATIC ON)",
                              "set(BUILD_ILMBASE_STATIC {})".format(not self.options.shared))
        if self.options.shared:
            tools.replace_in_file(os.path.join(self._source_subfolder, "OpenEXR", "IlmImf", "CMakeLists.txt"),
                                  "IlmBase::Half_static",
                                  "IlmBase::Half${OPENEXR_TARGET_SUFFIX}")
            tools.replace_in_file(os.path.join(self._source_subfolder, "OpenEXR", "IlmImf", "CMakeLists.txt"),
                                  "IlmBase::IlmThread_static",
                                  "IlmBase::IlmThread${OPENEXR_TARGET_SUFFIX}")
            tools.replace_in_file(os.path.join(self._source_subfolder, "OpenEXR", "IlmImf", "CMakeLists.txt"),
                                  "IlmBase::Iex_static",
                                  "IlmBase::Iex${OPENEXR_TARGET_SUFFIX}")
            # Do not override RUNTIME_DIR in IlmImf
            tools.replace_in_file(os.path.join(self._source_subfolder, "OpenEXR", "IlmImf", "CMakeLists.txt"),
                                  "SET(RUNTIME_DIR",
                                  "# SET(RUNTIME_DIR")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        with tools.chdir(os.path.join(self.package_folder, "lib")):
            for filename in glob.glob("*.la"):
                os.unlink(filename)

    def package_info(self):
        parsed_version = self.version.split(".")
        version_suffix = "-%s_%s" % (parsed_version[0], parsed_version[1]) if self.options.namespace_versioning else ""
        if not self.options.shared:
            version_suffix += "_s"
        if self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug":
            version_suffix += "_d"

        self.cpp_info.libs = ["IlmImf{}".format(version_suffix),
                              "IlmImfUtil{}".format(version_suffix),
                              "IlmThread{}".format(version_suffix),
                              "Iex{}".format(version_suffix),
                              "IexMath{}".format(version_suffix),
                              "Imath{}".format(version_suffix),
                              "Half{}".format(version_suffix)]

        self.cpp_info.includedirs = [os.path.join("include", "OpenEXR"), "include"]
        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("OPENEXR_DLL")

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
