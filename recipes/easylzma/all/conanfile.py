import os
from conan import ConanFile, tools
from conans import CMake


class EazylzmaConan(ConanFile):
    name = "easylzma"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lloyd/easylzma"
    description = ("An easy to use, tiny, public domain, C wrapper library around \
                    Igor Pavlov's work that can be used to compress and extract lzma files")
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    topics = ("conan", "eazylzma", "lzma")
    exports_sources = ["CMakeLists.txt", "patches/*"]
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _license_text(self):
        # Extract the License/s from the README to a file
        tmp = tools.files.load(self, os.path.join("source_subfolder", "README"))
        return tmp[tmp.find("License",1):tmp.find("work.", 1)+5]

    @property
    def _libname(self):
        return "easylzma" if self.options.shared else "easylzma_s"

    def config_options(self):
        if self.settings.os == "Windows":
           del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.files.patch(self, **patch)
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target=self._libname)

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._license_text)

        self.copy(pattern="*.dylib*", dst="lib", src="lib", keep_path=False, symlinks=True)
        self.copy(pattern="*.so*", dst="lib", src="lib", keep_path=False, symlinks=True)
        self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
        self.copy(pattern="*.a", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)

        self.copy("easylzma/*", dst="include", src=os.path.join(self._source_subfolder, "src"))

    def package_info(self):
        self.cpp_info.libs = [self._libname]
        if self.options.shared:
            self.cpp_info.defines = ["EASYLZMA_SHARED"]
        if self.settings.compiler == "Visual Studio":
            if "d" in str(self.settings.compiler.runtime):
                self.cpp_info.defines.append("DEBUG")
