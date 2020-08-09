from conans import ConanFile, CMake, tools
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
    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/*"
    _cmake_i = None

    @property
    def _cmake_install_folder(self):
        version = tools.Version(self.version)
        return "{}-{}.{}".format(self.name, version.major, version.minor)

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
            self._cmake_i.configure(build_folder=self._build_subfolder)
        return self._cmake_i

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

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        self._cmake.build()

    def package(self):
        self._cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", self._cmake_install_folder, "cmake"))

        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = [os.path.join("lib", self._cmake_install_folder, "include")]
        self.cpp_info.libdirs = [os.path.join("lib", self._cmake_install_folder)]
        objext = "obj" if self.settings.compiler == "Visual Studio" else "o"
        self.cpp_info.exelinkflags = [
            os.path.join(self.package_folder, "lib", self._cmake_install_folder, "mimalloc.{}".format(objext))]
        self.cpp_info.sharedlinkflags = [
            os.path.join(self.package_folder, "lib", self._cmake_install_folder, "mimalloc.{}".format(objext))]

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs.extend(["psapi", "shell32", "user32", "bcrypt"])
            elif self.settings.os == "Linux":
                self.cpp_info.system_libs.append("rt")
