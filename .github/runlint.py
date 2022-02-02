import os
import yaml
import requests
import packaging.version
import subprocess
import platform
import sys


def main(pr):
    session = requests.session()
    session.headers = {}
    token = os.getenv("GH_TOKEN")
    if token:
        session.headers["Authorization"] = "token %s" % token

    session.headers["Accept"] = "application/vnd.github.v3+json"
    session.headers["User-Agent"] = "request"
    session.auth = None
    # if user and pw:
    #    session.auth = requests.auth.HTTPBasicAuth(user, pw)

    github_server_url = os.getenv("GITHUB_SERVER_URL")
    github_repo = os.getenv("GITHUB_REPOSITORY")

    r = session.request("GET", f"{github_server_url}/{github_repo}/pull/{pr}.diff")
    r.raise_for_status()
    diff = r.text
    packages = set()
    for line in diff.split("\n"):
        if line.startswith("+++ b/recipes/") or line.startswith("--- a/recipes/"):
            parts = line.split("/")
            if len(parts) >= 5:
                packages.add(parts[2] + "/" + parts[3])
    for line in packages:
        package = line.split("/")[0]
        version = None
        folder = line.split("/")[1]
        with open(os.path.join("recipes", package, "config.yml"), "r") as file:
            config = yaml.safe_load(file)
            for v in config["versions"]:
                if config["versions"][v]["folder"] != folder:
                    continue
                try:
                    if not version or packaging.version.Version(v) > packaging.version.Version(version):
                        version = v
                except packaging.version.InvalidVersion:
                    print("Error parsing version %s for package %s in pr %s" % (v, package, pr))

        if version:
            shell = bool(platform.system() != "Windows")
            command = "conan export %s %s/%s@" % (os.path.join("recipes", package, folder), package, version)
            p = subprocess.run(command, shell=shell, check=False)

if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv[1])
