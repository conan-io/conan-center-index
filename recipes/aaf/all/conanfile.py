from conans import ConanFile, CMake, tools


class AafConan(ConanFile):
    name = "aaf"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/aaf/"
    description = "A  cross-platform SDK for AAF. AAF is a metadata management system and file format for use in professional multimedia creation and authoring."
    topics = ("aaf", "multimedia", "crossplatform")
    license = "AAF SDK PUBLIC SOURCE LICENSE"
    exports_sources = ["patches/**"]
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if tools.is_apple_os(self.settings.os):
            cmake = CMake(self, generator="Xcode")
        elif self.settings.compiler == "Visual Studio":
            cmake = CMake(self, generator="Visual Studio")
        else:
            cmake = CMake(self)

        cmake.definitions["PLATFORM"] = self.settings.compiler
        cmake.definitions["ARCH"] = "x86_64"
        cmake.configure(source_folder=self._source_subfolder)
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

