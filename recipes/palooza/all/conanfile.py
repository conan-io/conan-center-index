from conans import ConanFile, CMake, tools
import inspect


class PaloozaConan(ConanFile):
    name = "palooza"
    license = "<Put the package license here>"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/conan-io/conan-center-index"
    description = "<Description of Palooza here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"

    def source(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def build(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def package(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def package_info(self):
        raise Exception(inspect.currentframe().f_code.co_name)

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
        pass # 6
        #raise Exception(inspect.currentframe().f_code.co_name)

    def requirements(self):
        pass # 8
        #raise Exception(inspect.currentframe().f_code.co_name)

    def build_requirements(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def system_requirements(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def imports(self):
        raise Exception(inspect.currentframe().f_code.co_name)

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
