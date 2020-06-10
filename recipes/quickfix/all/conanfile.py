from conans import ConanFile, CMake, tools
import os


class QuickfixConan(ConanFile):
    name = "quickfix"
    license = "The QuickFIX Software License, Version 1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.quickfixengine.org"
    description = "QuickFIX is a free and open source implementation of the FIX protocol"
    topics = ("conan", "QuickFIX", "FIX", "Financial Information Exchange", "libraries", "cpp")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "ssl":  [True, False],
               "shared_ptr": ["std", "tr1"]}
    default_options = {"fPIC": True, "ssl": False, "shared_ptr": "std"}
    generators = "cmake"
    exports_sources = "patches/**"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def requirements(self):
        if self.options.ssl:
            self.requires("openssl/1.1.1g")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["HAVE_SSL"] = self.options.ssl
            self._cmake.definitions["SHARED_PTR"] = str(self.options.shared_ptr).upper()
            self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build(target="quickfix")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("config.h", dst="include", src=self._source_subfolder)
        self.copy("Except.h", dst="include", src=os.path.join(self._source_subfolder, "src", "C++"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.options.ssl:
            self.cpp_info.defines.append("HAVE_SSL=1")

        if self.options.shared_ptr == "std":
            self.cpp_info.defines.append("HAVE_STD_SHARED_PTR=1")
        else:
            self.cpp_info.defines.append("HAVE_STD_TR1_SHARED_PTR_FROM_TR1_MEMORY_HEADER=1")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32"])
