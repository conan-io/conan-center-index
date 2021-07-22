from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class AafConan(ConanFile):
    name = "aaf"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/aaf/"
    description = "A  cross-platform SDK for AAF. AAF is a metadata management system and file format for use in professional multimedia creation and authoring."
    topics = ("aaf", "multimedia", "crossplatform")
    license = "AAF SDK PUBLIC SOURCE LICENSE"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
            "shared": [True, False],
            "fPIC": [True, False]
            }
    default_options = {
            "shared": False,
            "fPIC": True
            }

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

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.runtime in ("MT", "MTd"):
            raise ConanInvalidConfiguration("Static runtime not supported")
        if self.settings.os == "Linux":
            raise ConanInvalidConfiguration("Linux not supported yet")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmake = CMake(self)

        if tools.is_apple_os(self.settings.os):
            cmake.definitions["PLATFORM"] = "apple-clang"
        elif self.settings.compiler == "Visual Studio":
            cmake.definitions["PLATFORM"] = "vc"
        else:
            cmake.definitions["PLATFORM"] = self.settings.os

        cmake.definitions["ARCH"] = "x86_64"
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

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
