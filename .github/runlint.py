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
            packages.add(line.split("/")[2])
    for package in packages:
        version = packaging.version.Version("0.0.0")
        folder = ""
        with open(os.path.join("recipes", package, "config.yml"), "r") as file:
            config = yaml.safe_load(file)
            for v in config["versions"]:
                try:
                    tmpVer = packaging.version.Version(v)
                    if tmpVer > version:
                        version = tmpVer
                        folder = config["versions"][v]["folder"]
                except packaging.version.InvalidVersion:
                    print("Error parsing version %s for package %s in pr %s" % (v, package, pr))

        shell = bool(platform.system() != "Windows")
        command = "conan export %s %s/%s@" % (os.path.join("recipes", package, folder), package, version)
        p = subprocess.run(command, shell=shell, check=True)

if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv[1])
