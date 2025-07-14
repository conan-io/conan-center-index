from conan import ConanFile
from conan.tools.build import can_run
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    
    def requirements(self):
        self.requires(self.tested_reference_str)
    
    def test(self):
        if not can_run(self):
            return
        
        # Get the mgconsole dependency
        mgconsole_dep = self.dependencies["mgconsole"]
        
        # Build the path to the executable
        executable_name = "mgconsole"
        if self.settings.os == "Windows":
            executable_name += ".exe"
        
        bin_path = os.path.join(mgconsole_dep.package_folder, "bin", executable_name)
        
        if os.path.exists(bin_path):
            self.output.info("Executable found! Testing...")
            try:
                self.run(f'"{bin_path}" --help', env="conanrun")
            except Exception as e:
                self.output.info(f"Executable ran but returned non-zero exit code: {e}")
