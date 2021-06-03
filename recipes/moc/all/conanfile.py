from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from os import rename
from os.path import join
from shutil import move
from glob import glob

class MocConan(ConanFile):
    _requirements = [
        "flex/2.6.4",
        "bison/3.7.1"
    ]
    name = "moc"
    homepage = "https://www.github.com/zuut/moc"
    description = "Moc, the marked-up object compiler"
    topics = ("conan", "moc", "idl", "code generation")
    url = "https://github.com/conan-io/conan-center-index"
    # see https://spdx.dev/licenses/
    license = "Apache-2.0"    
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _cmake = None

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("%s package is not compatible with Windows." % self.name)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        #os.rename(self.name + "-" + self.version, self._source_subfolder)
        rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_CXX_STANDARD"] = 17
        self._cmake.definitions["Verbose"] = True
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def requirements(self):
        for req in self._requirements:
            print( "override requirement: %s" % req )
            self.requires(req)

    def package(self):
        # export CMAKE_INSTALL_PREFIX=???
        # cmake --build . --target install
        cmake = self._configure_cmake()
        cmake.install()
        for file in glob(self.package_folder + "/lib/**/*-config.cmake") :
            print("conan forbids having file %s " % file )
            move(file, file + "-sample")
        #for file in glob(self.package_folder + "/lib/**/*.cmake") :
        #    print("Moving file '%s' to cmake-modules folder"%file)
        #    move(file, self.package_folder + "/cmake-modules")
        move(self.package_folder + "/cmake-modules",
             self.package_folder + "/lib/cmake-modules")
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder,
                  keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["uf"]
        self.env_info.MOC_TOOL = join(self.package_folder, "bin", "moc").replace("\\", "/")

        self.env_info.PATH.append(join(self.package_folder, "bin"))

        self.env_info.CMAKE_MODULE_PATH.append(join(self.package_folder, "lib", "cmake-modules"))
        self.env_info.CMAKE_MODULE_PATH.append(join(self.package_folder, "lib", "moc"))
        self.env_info.CMAKE_MODULE_PATH.append(join(self.package_folder, "lib", "uf"))
        self.cpp_info.names["cmake_find_package"] = "Moc"
        self.cpp_info.names["cmake_find_package_multi"] = "Moc"

        self.cpp_info.builddirs.append(join("lib", "cmake-modules"))
        self.cpp_info.builddirs.append(join("lib", "moc"))
        self.cpp_info.builddirs.append(join("lib", "uf"))
        self.cpp_info.libs = tools.collect_libs(self)
