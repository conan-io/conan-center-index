from conan import ConanFile
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.layout import basic_layout
from conan.tools.scm import Git

class CriterionConan(ConanFile):
    name = "criterion"
    version = "2.4.1"
    license = "MIT"
    topics = ("testing")
    description = "A cross-platform C and C++ unit testing framework for the 21st century"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def source(self):
        git = Git(self)
        git.clone("https://github.com/Snaipe/Criterion.git", target=".", 
                  args=['--recurse-submodules', '--depth', '1', '--branch', f'v{self.version}'])

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):        
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options['force_fallback_for'] = ['boxfort']
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        meson = Meson(self)
        meson.install()

    def package_info(self):
        self.cpp_info.libs = ["criterion"]
