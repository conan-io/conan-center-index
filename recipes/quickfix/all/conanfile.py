from conans import ConanFile, CMake, tools
import shutil
import os
import re


class QuickfixConan(ConanFile):
    name = "quickfix"
    license = "The QuickFIX Software License, Version 1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.quickfixengine.org"
    description = "QuickFIX is a free and open source implementation of the FIX protocol"
    topics = ("conan", "QuickFIX", "FIX", "Financial Information Exchange", "libraries", "cpp")
    settings = "os", "compiler", "build_type", "arch"
    options = {"ssl": [True, False], "fPIC": [True, False]}
    default_options = {"ssl": False, "fPIC": True}
    generators = "cmake"
    file_pattern = re.compile(r'quickfix-(.*)')
    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "quickfix"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        files = os.listdir()
        match_dirs = list(filter(self.file_pattern.search, files))
        extracted_dir = match_dirs[0]
        os.rename(extracted_dir, self._source_subfolder)

        os.makedirs(f"{self._source_subfolder}/include")
        shutil.copyfile(f"{self._source_subfolder}/src/C++/Except.h",
                        f"{self._source_subfolder}/include/Except.h")

    def requirements(self):
        if self.options.ssl:
            self.requires("openssl/1.1.1g")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build(target="quickfix")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("config.h", dst="include", src=self._source_subfolder)
        self.copy("Except.h", dst="include", src=f"{self._source_subfolder}/src/C++")
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        shutil.rmtree(f"{self.package_folder}{os.sep}share")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Windows":
            self.cpp_info.libs.append("wsock32")

    def _configure_cmake(self):
        cmake = CMake(self)

        if self.options.ssl:
            cmake.definitions["HAVE_SSL"] = "ON"

        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
