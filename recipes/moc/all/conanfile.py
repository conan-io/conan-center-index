from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from os import rename
from os.path import isdir, join
from shutil import move
from glob import glob
from distutils.version import LooseVersion

class MocConan(ConanFile):
    name = "moc"
    homepage = "https://www.github.com/zuut/moc"
    description = "Moc, the marked-up object compiler"
    topics = ("conan", "moc", "idl", "code generation")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"    
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = { "fPIC": [True, False] }
    default_options = { "fPIC": True }
    _cmake = None
    _supported_compilers = [
        ("Linux", "gcc", "6"),
        ("Linux", "clang", "6"),
        ("Macos", "gcc", "6"),
        ("Macos", "clang", "6")
    ]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if not self._check_compiler():
            raise ConanInvalidConfiguration("%s package is not compatible with os %s and compiler %s version %s." % (self.name, self.settings.os, self.settings.compiler, self.settings.compiler.version))

    def _check_compiler(self):
        os = self.settings.os
        compiler = self.settings.compiler
        compiler_version = tools.Version(compiler.version)
        return any(os == sc[0] and compiler == sc[1] and compiler_version >= sc[2] for sc in self._supported_compilers)

    def build_requirements(self):
        self.build_requires("flex/2.6.4")
        self.build_requires("bison/3.7.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.remove_files_by_mask(join(self.package_folder, "lib"), "*-config.cmake")
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder,
                  keep_path=False)
        cmakeModulesDir=join(self.package_folder, "cmake-modules")
        if isdir(cmakeModulesDir):
            move(cmakeModulesDir,join(self.package_folder, "lib/cmake"))
        return

    def package_info(self):
        self.env_info.MOC_TOOL = join(self.package_folder, "bin", "moc").replace("\\", "/")

        self.env_info.PATH.append(join(self.package_folder, "bin"))

        self.cpp_info.names["cmake_find_package"] = "Moc"
        self.cpp_info.names["cmake_find_package_multi"] = "Moc"

        self.cpp_info.build_modules.append(join("lib", "cmake", "BisonFlex.cmake"))
        self.cpp_info.build_modules.append(join("lib", "cmake", "Moc.cmake"))
        self.cpp_info.builddirs.append(join("lib", "cmake"))
        self.cpp_info.builddirs.append(join("lib", "moc"))
        self.cpp_info.builddirs.append(join("lib", "uf"))
        self.cpp_info.libs = tools.collect_libs(self)
