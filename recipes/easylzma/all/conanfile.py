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
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
           del self.options.fPIC

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

        # Extract the License/s from the README to a file
        tmp = tools.load("source_subfolder/README")
        license_contents = tmp[tmp.find("License",1):tmp.find("work.", 1)+5]
        tools.save("LICENSE", license_contents)
        # Package it
        self.copy("LICENSE*", dst="licenses",  ignore_case=True, keep_path=False)

        # Copy static and dynamic libs
        build_dir = os.path.join(self._source_subfolder,self.name + "-" + self.version)
        if self.options.shared:
            self.copy(pattern="*.dylib*", dst="lib", src=build_dir, keep_path=False, symlinks=True)
            self.copy(pattern="*.so*", dst="lib", src=build_dir, keep_path=False, symlinks=True)
            self.copy(pattern="*.dll", dst="bin", src=build_dir, keep_path=False)
            self.copy(pattern="*.dll.a", dst="lib", src=build_dir, keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", src=build_dir, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=build_dir, keep_path=False)

        # Copy headers
        self.copy("*", dst="include", src=os.path.join(self._source_subfolder,self.name + "-" + self.version,"include"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
