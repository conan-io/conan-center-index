from conans import ConanFile, CMake, tools
import os


class MsgpackConan(ConanFile):
    name = "msgpack"
    description = "The official C++ library for MessagePack"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/msgpack/msgpack-c"
    topics = ("conan", "msgpack", "message-pack", "serialization")
    license = "BSL-1.0"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"
    options = {"fPIC": [True, False], "shared": [True, False], "header_only": [True, False], "with_boost": [True, False]}
    default_options = {"fPIC": True, "shared": False, "header_only": False, "with_boost": False}

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.header_only:
            self.settings.clear()
            del self.options.shared
            del self.options.fPIC
            del self.options.with_boost

    def requirements(self):
        if not self.options.header_only and self.options.with_boost:
            self.requires.add("boost/1.69.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "msgpack-c-cpp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["MSGPACK_BOOST"] = self.options.with_boost
        cmake.definitions["MSGPACK_32BIT"] = self.settings.arch == "x86"
        cmake.definitions["MSGPACK_BUILD_EXAMPLE"] = False
        cmake.definitions["MSGPACK_BUILD_TESTS"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        if not self.options.header_only:
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy("LICENSE_1_0.txt", dst="licenses", src=self._source_subfolder)
        if self.options.header_only:
            self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
            self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        else:
            cmake = self._configure_cmake()
            cmake.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if self.options.header_only:
            self.info.header_only()
        else:
            self.cpp_info.libs = tools.collect_libs(self)
