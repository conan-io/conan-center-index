import os
from conans import ConanFile, tools, CMake

class eazylzmaConan(ConanFile):
    name = "easylzma"
    license = "Public Domain"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lloyd/easylzma"
    description = ("An easy to use, tiny, public domain, C wrapper library around \
                    Igor Pavlov's work that can be used to compress and extract lzma files")
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    topics = ("conan", "eazylzma", "lzma")
    exports_sources = ["CMakeLists.txt", "patches/*"]
    exports = ["LICENSE"]
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self.source_folder)
        self.copy("*.so*", dst="lib", src=os.path.join(self._source_subfolder,self.name + "-" + self.version,"lib"))
        self.copy("*.dll", dst="lib", src=os.path.join(self._source_subfolder,self.name + "-" + self.version,"lib", str(self.settings.build_type)))
        self.copy("*.dylib", dst="lib", src=os.path.join(self._source_subfolder,self.name + "-" + self.version,"lib"))
        self.copy("*.a", dst="lib", src=os.path.join(self._source_subfolder,self.name + "-" + self.version,"lib"))
        self.copy("*.lib", dst="lib", src=os.path.join(self._source_subfolder,self.name + "-" + self.version,"lib", str(self.settings.build_type)))
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder,self.name + "-" + self.version,"include"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
