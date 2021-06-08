from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from os import rename
from os.path import isdir, join
from shutil import move
from glob import glob
from distutils.version import LooseVersion

class MocConan(ConanFile):
    _noCmakeConfigFiles = True
    _requirements = [
        "flex/2.6.4",
        "bison/3.7.1"
    ]
    _supported_compilers = [
        ("Linux", "gcc", "6"),
        ("Linux", "clang", "6"),
        ("Macos", "gcc", "6"),
        ("Macos", "clang", "6"),
        #("Macos", "apple-clang", "10")
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

    # picks a reasonable version if not specified
    @property
    def _version(self):
        if hasattr(self, "version") and self.version != None:
            return self.version
        if hasattr(self, "_default_version") and self._default_version != None:
            self.version = self._default_version
            return self.version
        # default to the latest version
        vmax="0"
        lvmax = LooseVersion(vmax)
        for v in self.conan_data["sources"]:
            lv = LooseVersion(v)
            try:
                if lv > lvmax:
                    vmax = v
                    lvmax = LooseVersion(vmax)
            except:
                print("unable to compare %s to %s" %(lv,lvmax))
        self.version = vmax
        return self.version    

    @property
    def _source_fullpath(self):
        src_dir= join(self.source_folder,
                      self._source_subfolder).replace("\\", "/")
        print("Source='%s'" % src_dir)
        return src_dir

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        print("do config_options for %s" % self._version)
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        print("do configure for %s" % self._version)
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if not self._check_compiler():
            raise ConanInvalidConfiguration("%s package is not compatible with os %s and compiler %s version %s." % (self.name, self.settings.os, self.settings.compiler, self.settings.compiler.version))

    def _check_compiler(self):
        os = self.settings.os
        compiler = self.settings.compiler
        compiler_version = tools.Version(compiler.version)
        return any(os == sc[0] and compiler == sc[1] and compiler_version >= sc[2] for sc in self._supported_compilers)

    def requirements(self):
        print("calc requirements for %s" % self._version)
        for req in self._requirements:
            print( "override requirement: %s" % req )
            self.requires(req)

    # Retrieve the source code.
    def source(self):
        print("Retrieving source for moc/%s@" % self._version)
        tools.get(**self.conan_data["sources"][self._version])
        rename(self.name + "-" + self._version, self._source_fullpath)

    # builds the project items
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

    # the installs the project items
    def package(self):
        # export CMAKE_INSTALL_PREFIX=???
        # cmake --build . --target install
        cmake = self._configure_cmake()
        cmake.install()
        if self._noCmakeConfigFiles:
            for file in glob(self.package_folder + "/lib/**/*-config.cmake") :
                print("conan forbids having file %s " % file )
                move(file, file + "-sample")
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder,
                  keep_path=False)
        cmakeModulesDir=join(self.package_folder, "cmake-modules")
        if isdir(cmakeModulesDir):
            move(cmakeModulesDir,join(self.package_folder, "lib/cmake"))
        return

    def package_info(self):
        self.cpp_info.libs = ["uf"]
        self.env_info.MOC_TOOL = join(self.package_folder, "bin", "moc").replace("\\", "/")

        self.env_info.PATH.append(join(self.package_folder, "bin"))

        self.env_info.CMAKE_MODULE_PATH.append(join(self.package_folder, "lib", "cmake"))
        self.env_info.CMAKE_MODULE_PATH.append(join(self.package_folder, "lib", "moc"))
        self.env_info.CMAKE_MODULE_PATH.append(join(self.package_folder, "lib", "uf"))
        self.cpp_info.names["cmake_find_package"] = "Moc"
        self.cpp_info.names["cmake_find_package_multi"] = "Moc"

        self.cpp_info.builddirs.append(join("lib", "cmake"))
        self.cpp_info.builddirs.append(join("lib", "moc"))
        self.cpp_info.builddirs.append(join("lib", "uf"))
        self.cpp_info.libs = tools.collect_libs(self)
