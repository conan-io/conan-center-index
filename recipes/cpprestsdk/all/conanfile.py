from conans import ConanFile, CMake, tools
import os


class CppRestSDKConan(ConanFile):
    name = "cpprestsdk"
    description = "A project for cloud-based client-server communication in native code using a modern asynchronous " \
                  "C++ API design"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Microsoft/cpprestsdk"
    topics = ("conan", "cpprestsdk", "rest", "client", "http", "https")
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_websockets": [True, False],
        "with_compression": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_websockets": True,
        "with_compression": True
    }
    short_paths = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("openssl/1.1.1g")
        if self.options.with_compression:
            self.requires("zlib/1.2.11")
        if self.options.with_websockets:
            self.requires("websocketpp/0.8.2")
        self.requires("boost/1.72.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self, set_cmake_flags=True)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_SAMPLES"] = False
        self._cmake.definitions["WERROR"] = False
        self._cmake.definitions["CPPREST_EXCLUDE_WEBSOCKETS"] = not self.options.with_websockets
        self._cmake.definitions["CPPREST_EXCLUDE_COMPRESSION"] = not self.options.with_compression
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_clang_libcxx(self):
        if self.settings.compiler == 'clang' and str(self.settings.compiler.libcxx) in ['libstdc++', 'libstdc++11']:
            tools.replace_in_file(os.path.join(self._source_subfolder, 'Release', 'CMakeLists.txt'),
                                  'libc++', 'libstdc++')

    def build(self):
        if "patches" in self.conan_data and self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)
        self._patch_clang_libcxx()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cpprestsdk"))

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            debug_suffix = 'd' if self.settings.build_type == 'Debug' else ''
            toolset = {'12': '120',
                       '14': '140',
                       '15': '141',
                       '16': '142'}.get(str(self.settings.compiler.version))
            version_tokens = self.version.split(".")
            versioned_name = "cpprest%s_%s_%s%s" % (toolset, version_tokens[0], version_tokens[1], debug_suffix)
            # CppRestSDK uses different library name depends on CMAKE_VS_PLATFORM_TOOLSET
            if not os.path.isfile(os.path.join(self.package_folder, 'lib', '%s.lib' % versioned_name)):
                versioned_name = "cpprest_%s_%s%s" % (version_tokens[0], version_tokens[1], debug_suffix)
            lib_name = versioned_name
        else:
            lib_name = 'cpprest'

        self.cpp_info.libs.append(lib_name)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["winhttp", "httpapi", "bcrypt"])
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["CoreFoundation", "Security"])
        if not self.options.shared:
            self.cpp_info.defines.append("_NO_ASYNCRTIMP")
