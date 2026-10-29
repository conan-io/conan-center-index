from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.env import Environment
from conan.tools.files import save
import os
import textwrap


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        openssl_pkg = self.dependencies["openssl"].package_folder.replace("\\", "/")
        fipsmodule_cnf = f"{openssl_pkg}/ssl/fipsmodule.cnf"
        cnf = textwrap.dedent(f"""\
            config_diagnostics = 1
            openssl_conf = openssl_init
            .include {fipsmodule_cnf}

            [openssl_init]
            providers = provider_sect

            [provider_sect]
            fips = fips_sect
            base = base_sect

            [base_sect]
            activate = 1
        """)
        cnf_path = os.path.join(self.generators_folder, "openssl_fips.cnf")
        save(self, cnf_path, cnf)

        env = Environment()
        env.define("OPENSSL_CONF", cnf_path.replace("\\", "/"))
        env.vars(self, scope="run").save_script("openssl_conf")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
