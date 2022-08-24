from conan.tools.files import apply_conandata_patches
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import glob


class AafConan(ConanFile):
    name = "aaf"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/aaf/"
    description = "A cross-platform SDK for AAF. AAF is a metadata management system and file format for use in professional multimedia creation and authoring."
    topics = ("aaf", "multimedia", "crossplatform")
    license = "AAFSDKPSL-2.0"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "structured_storage": [True, False],
    }
    default_options = {
        "structured_storage": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("expat/2.4.1")
        self.requires("libjpeg/9d")
        if self.settings.os in ("FreeBSD", "Linux"):
            self.requires("libuuid/1.0.3")

    def validate(self):
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("ARM v8 not supported")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        apply_conandata_patches(self)

        cmake = CMake(self)

        if tools.is_apple_os(self.settings.os):
            cmake.definitions["PLATFORM"] = "apple-clang"
        elif self.settings.compiler == "Visual Studio":
            cmake.definitions["PLATFORM"] = "vc"
        else:
            cmake.definitions["PLATFORM"] = self.settings.os

        cmake.definitions["ARCH"] = "x86_64"  # ARCH is used only for setting the output directory. So itsvalue does not matter here.
        cmake.definitions["AAF_NO_STRUCTURED_STORAGE"] = not self.options.structured_storage
        cmake.configure(build_folder=self._build_subfolder)
        cmake.build()

    def package(self):
        self.copy("out/shared/include/*.h", dst="include", src=self._source_subfolder, keep_path=False)
        self.copy("out/target/*/*/RefImpl/*.dll", dst="bin", src=self._source_subfolder, keep_path=False)
        self.copy("out/target/*/*/RefImpl/*.lib", dst="lib", src=self._source_subfolder, keep_path=False)
        self.copy("out/target/*/*/RefImpl/*.so", dst="lib", src=self._source_subfolder, keep_path=False)
        self.copy("out/target/*/*/RefImpl/*.dylib", dst="lib", src=self._source_subfolder, keep_path=False)
        self.copy("out/target/*/*/RefImpl/*.a", dst="lib", src=self._source_subfolder, keep_path=False)
        self.copy("LEGAL/AAFSDKPSL.TXT", dst="licenses", src=self._source_subfolder, keep_path=False)

        if tools.is_apple_os(self.settings.os):
            with tools.chdir(os.path.join(self.package_folder, "lib")):
                for dylib in glob.glob("*.dylib"):
                    command = "install_name_tool -id {0} {1}".format(os.path.basename(dylib), dylib)
                    self.output.info(command)
                    self.run(command)

    def package_info(self):
        if self.settings.os == "Windows":
            if self.settings.build_type == "Release":
                self.cpp_info.libs = ["AAF", "AAFIID", "AAFCOAPI"]
            else:
                self.cpp_info.libs = ["AAFD", "AAFIIDD", "AAFCOAPI"]
        else:
            self.cpp_info.libs = ["aaflib", "aafiid", "com-api"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["dl"]
        if self.settings.os == 'Macos':
            self.cpp_info.frameworks = ['CoreServices', 'CoreFoundation']
