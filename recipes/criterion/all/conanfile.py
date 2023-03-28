from os import path
from conan import ConanFile
from conan.tools.files import get
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson

class CriterionConan(ConanFile):
    name = "criterion"
    version = "2.4.1"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Snaipe/Criterion"
    topics = ("testing")
    description = "A cross-platform C and C++ unit testing framework for the 21st century"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    requires = ("libgit2/[>=1.0]", "libffi/[~3.4]")

    def source(self):
        print(path.join(self.source_folder, 'dependencies', 'debugbreak'))
        get(self, url=self.conan_data["sources"][self.version]['url'], sha256=self.conan_data["sources"][self.version]['sha256'], strip_root=True)

        # We need to get dependencies for building, they are git submodules!
        get(self, self.conan_data["sources"][self.version]['debugbreak_url'], 
            sha256=self.conan_data["sources"][self.version]['debugbreak_sha256'], 
            destination=path.join(self.source_folder, 'dependencies', 'debugbreak'),
            strip_root=True)
        
        get(self, self.conan_data["sources"][self.version]['klib_url'], 
            sha256=self.conan_data["sources"][self.version]['klib_sha256'], 
            destination=path.join(self.source_folder, 'dependencies', 'klib'),
            strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):        
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        pc = PkgConfigDeps(self)
        pc.generate()

        tc = MesonToolchain(self)
        tc.project_options['force_fallback_for'] = ['boxfort']
        
        # We don't need tests or samples
        tc.project_options['tests'] = False
        tc.project_options['samples'] = False
        
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

    def build_requirements(self):
        self.tool_requires("pkgconf/[~1.9.3]")
        self.tool_requires("meson/[>=0.51.2]")
