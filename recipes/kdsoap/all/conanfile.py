from conans import ConanFile, CMake, tools
import os


class KdsoapConan(ConanFile):
    name = "kdsoap"
    license = (
        "https://raw.githubusercontent.com/KDAB/KDSoap/kdsoap-{0}-release/LICENSE.txt,"
        "https://raw.githubusercontent.com/KDAB/KDSoap/kdsoap-{0}-release/LICENSE.AGPL3-modified.txt,"
        "https://raw.githubusercontent.com/KDAB/KDSoap/kdsoap-{0}-release/LICENSE.GPL.txt,"
        "https://raw.githubusercontent.com/KDAB/KDSoap/kdsoap-{0}-release/LICENSE.LGPL.txt").format("master")
    author = "Klaralvdalens Datakonsult AB (KDAB) info@kdab.com"
    exports_sources = ["CMakeLists.txt"]
    url = "https://github.com/KDAB/KDSoap.git"
    description = "KD Soap is a Qt-based client-side and server-side SOAP component."
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    _source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires("qt/5.13.2@bincrafters/stable")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("KDSoap-{}-{}-release".format(self.name,
                                                self.version), self._source_subfolder)
        self._patch_cmake()

    def _patch_cmake(self):
        # Patch cmake to make sure that files will be installed
        cmake_file = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(
            cmake_file,
            "if(CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)",
            "if(1)")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE*", dst="licenses",
                  src=self._source_subfolder, keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs.sort(reverse=True)
