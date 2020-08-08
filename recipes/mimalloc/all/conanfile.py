from conans import ConanFile, CMake, MSBuild, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os


class MimallocConan(ConanFile):
    name = "mimalloc"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/mimalloc"
    description = "mimalloc is a compact general purpose allocator with excellent performance."
    topics = ("libraries", "c", "c++", "malloc", "allocator")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False],
               "override": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False,
                       "override": True}
    generators = "cmake", "visual_studio"
    exports_sources = "patches/**"
    _cmake_i = None
    _msbuild_i = None

    @property
    def _cmake_install_folder(self):
        p1 = self.version.find(".")
        if p1 != -1:
            p2 = self.version.find(".", p1 + 1)
            if p2 != -1:
                return self.name + "-" + self.version[0:p2]
            else:
                return self.name + "-" + self.version
        else:
            return self.name + "-" + self.version

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _cmake(self):
        if not self._cmake_i:
            self._cmake_i = CMake(self)
            self._cmake_i.definitions["MI_BUILD_TESTS"] = False
            self._cmake_i.definitions["MI_BUILD_SHARED"] = self.options.shared
            self._cmake_i.definitions["MI_BUILD_STATIC"] = not self.options.shared
            self._cmake_i.configure(source_folder=self._source_subfolder,
                build_folder=self._build_subfolder)
        return self._cmake_i

    @property
    def _msbuild(self):
        if not self._msbuild_i:
            self._msbuild_i = MSBuild(self)
        return self._msbuild_i

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("mimalloc-" + self.version, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "14")
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            if Version(self.settings.compiler.version) < "15":
                raise ConanInvalidConfiguration("Visual Studio 15 2017 or newer is required")

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        if self.settings.compiler == "Visual Studio":
            target = "mimalloc-override" if self.options.shared else "mimalloc"
            if Version(self.settings.compiler.version) >= "16":
                self._msbuild.build(
                    os.path.join(self._source_subfolder, "ide", "vs2019", "mimalloc.sln"),
                    targets=[target])
            else:
                self._msbuild.build(
                    os.path.join(self._source_subfolder, "ide", "vs2017", "mimalloc.sln"),
                    targets=[target])
        else:
            self._cmake.build()

    def package(self):
        if self.settings.compiler == "Visual Studio":
            self.copy("*.h", dst="include",
                src=os.path.join(self._source_subfolder, "include"))
            self.copy("*.lib", dst="lib",
                src=os.path.join(self._source_subfolder, "out"),
                keep_path=False)
            self.copy("*.dll", dst="bin",
                src=os.path.join(self._source_subfolder, "out"),
                keep_path=False)
        else:
            self._cmake.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", self._cmake_install_folder, "cmake"))

        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler != "Visual Studio":
            self.cpp_info.includedirs = [
                os.path.join("lib", self._cmake_install_folder, "include")]
