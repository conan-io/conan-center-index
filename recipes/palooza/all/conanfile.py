from conans import ConanFile, CMake, tools
import inspect
import os


class PaloozaConan(ConanFile):
    name = "palooza"
    license = "<Put the package license here>"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/conan-io/conan-center-index"
    description = "<Description of Palooza here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        pass # 13
        # raise Exception(inspect.currentframe().f_code.co_name)

    def build(self):
        pass # 15
        # raise Exception(inspect.currentframe().f_code.co_name)

    def touch(self, filename):
        with open(filename, "w") as f:
            f.write("")

    def package(self):
        with tools.chdir(self.package_folder):
            tools.mkdir("licenses")
            tools.mkdir("lib")
            tools.mkdir("bin")
            tools.mkdir("include")
            self.touch(os.path.join("include", "test.h"))
            self.touch(os.path.join("licenses", "LICENSE"))
            names = []
            if self.settings.os == "Windows":
                names = [os.path.join("lib", "mylib.lib")]
                if self.options.shared:
                    names.append(os.path.join("bin", "mylib.dll"))
            if self.settings.os == "Linux":
                if self.options.shared:
                    names = [os.path.join("lib", "libmylib.a")]
                else:
                    names = [os.path.join("lib", "libmylib.so")]
            if self.settings.os == "Macos":
                if self.options.shared:
                    names = [os.path.join("lib", "libmylib.a")]
                else:
                    names = [os.path.join("lib", "libmylib.dylib")]
            for name in names:
                self.touch(name)
        pass # 16
        # raise Exception(inspect.currentframe().f_code.co_name)

    def package_info(self):
        pass # 17?
        # raise Exception(inspect.currentframe().f_code.co_name)

    def set_name(self):
        pass # 2
        #raise Exception(inspect.currentframe().f_code.co_name)

    def set_version(self):
        pass # 3
        #raise Exception(inspect.currentframe().f_code.co_name)

    def configure(self):
        pass # 7
        #raise Exception(inspect.currentframe().f_code.co_name)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        pass # 6
        #raise Exception(inspect.currentframe().f_code.co_name)

    def requirements(self):
        pass # 8
        #raise Exception(inspect.currentframe().f_code.co_name)

    def build_requirements(self):
        pass # 11
        # raise Exception(inspect.currentframe().f_code.co_name)

    def system_requirements(self):
        pass # 12
        #raise Exception(inspect.currentframe().f_code.co_name)

    def imports(self):
        pass # 14
        # raise Exception(inspect.currentframe().f_code.co_name)

    def package_id(self):
        pass # 9
        #raise Exception(inspect.currentframe().f_code.co_name)

    def build_id(self):
        pass # 10
        #raise Exception(inspect.currentframe().f_code.co_name)

    def deploy(self):
        raise Exception(inspect.currentframe().f_code.co_name)
        
    def init(self):
        pass # 1
        #raise Exception(inspect.currentframe().f_code.co_name)

    def export(self):
        pass # 4
        #raise Exception(inspect.currentframe().f_code.co_name)
        
    def export_sources(self):
        pass # 5
        #raise Exception(inspect.currentframe().f_code.co_name)

    def test(self):
        raise Exception(inspect.currentframe().f_code.co_name)
