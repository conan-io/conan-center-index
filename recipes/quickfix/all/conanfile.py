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

        self._patch_sources()

    def requirements(self):
        if self.options.ssl:
            self.requires("openssl/1.1.1g")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        cmake = self._configure_cmake()
        cmake.build(target="quickfix")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("config.h", dst="include", src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Windows":
            self.cpp_info.libs.append("wsock32")

            if self.options.ssl and not self.options["openssl"].shared:
                self.cpp_info.libs.append("crypt32")

    def _configure_cmake(self):
        cmake = CMake(self)

        if self.options.ssl:
            cmake.definitions["HAVE_SSL"] = "ON"

        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        if self.options.ssl and not self.options["openssl"].shared:
            tools.replace_in_file(f"{self._source_subfolder}/src/C++/CMakeLists.txt",
                                  "  target_link_libraries(${PROJECT_NAME} ${OPENSSL_LIBRARIES} ${MYSQL_CLIENT_LIBS} "
                                  "${PostgreSQL_LIBRARIES} ws2_32)",
                                  "  target_link_libraries(${PROJECT_NAME} ${OPENSSL_LIBRARIES} ${MYSQL_CLIENT_LIBS} "
                                  "${PostgreSQL_LIBRARIES} ws2_32 crypt32)")
