from conans import ConanFile, tools, MSBuild
import os


class MpirConan(ConanFile):
    name = "mpir"
    description = "MPIR is a highly optimised library for bignum arithmetic" \
                  "forked from the GMP bignum library."
    topics = ("conan", "mpir", "multiprecision", "math", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mpir.org/"
    license = "LGPL v3+"
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"

    def build_requirements(self):
        self.build_requires("yasm/1.3.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        # maybe configure architecture

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            dll_or_lib = "dll" if self.options.shared else "lib"
            vcxproj_path = os.path.join(self._source_subfolder,
                                        "build.vc{}".format(self.settings.compiler.version),
                                        "{}_mpir_gc".format(dll_or_lib),
                                        "{}_mpir_gc.vcxproj".format(dll_or_lib))
            self.output.info(vcxproj_path)
            msbuild = MSBuild(self)
            msbuild.build(vcxproj_path)
            #TODO handle runtime

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)        
        lib_folder = os.path.join(self._source_subfolder,
                                  "lib", "x64", str(self.settings.build_type))
        self.copy("*.h", dst="include", src=lib_folder, keep_path=True)
        self.copy(pattern="*.dll*", dst="bin", src=lib_folder, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=lib_folder, keep_path=False)        

    def package_info(self):
        self.cpp_info.libs = ['mpir']
