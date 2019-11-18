from conans import ConanFile, CMake, tools
import os


class DocoptCppConan(ConanFile):
    name = "docopt.cpp"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/docopt/docopt.cpp"
    settings = "os", "compiler", "build_type", "arch"
    description = "C++11 port of docopt"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    topics = ("CLI")
    generators = 'cmake'
    exports_sources = ['patches/**', 'CMakeLists.txt']
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = CMake(self)
        # docopt's cmakelists actually ignores BUILD_SHARED_LIBS and builds both
        # libs everytime. This makes conan export two targets with the same name
        # which is illegal. To work around this, we install in a stage folder
        # and we take only the lib we want.
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = "stage"
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        stage_dir = "stage"

        self.copy("include/*", src=stage_dir, excludes=("*docopt_private.h", "*docopt_util.h"))
        if self.options.shared:
            self.copy("*.so*", src=stage_dir, dst="lib", symlinks=True, keep_path=False)
            self.copy("*.dylib", src=stage_dir, dst="lib", symlinks=True, keep_path=False)
            self.copy("*.dll", src=stage_dir, dst="bin", keep_path=False)
            self.copy("*docopt.lib", src=stage_dir, dst="lib", keep_path=False)
        else:
            self.copy("*.a", src=stage_dir, dst="lib", keep_path=False)
            self.copy("*docopt_s.lib", src=stage_dir, dst="lib", keep_path=False)
        self.copy("*LICENSE*", dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
