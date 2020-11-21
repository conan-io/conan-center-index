from conans import ConanFile, CMake, tools
import inspect


class PaloozaConan(ConanFile):
    name = "palooza"
    version = "1.0"
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
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
        raise Exception(inspect.currentframe().f_code.co_name)

    def set_version(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def configure(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def config_options(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def requirements(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def build_requirements(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def system_requirements(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def imports(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def package_id(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def build_id(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def deploy(self):
        raise Exception(inspect.currentframe().f_code.co_name)
        
    def init(self):
        pass # 1
        #raise Exception(inspect.currentframe().f_code.co_name)

    def export(self):
        raise Exception(inspect.currentframe().f_code.co_name)
        
    def export_sources(self):
        raise Exception(inspect.currentframe().f_code.co_name)

    def test(self):
        raise Exception(inspect.currentframe().f_code.co_name)
