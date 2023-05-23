#include <cstdio>
#include <semver/version.hh>
#include <string>

int main() {
  auto const ver_data = std::string{"1.3.0-beta.5+something.mixed.5"};
  semver::project_version beta5{ver_data};

  auto const ver_data_rc = std::string{"1.3.0-rc"};
  semver::project_version rc{ver_data_rc};

  char const *verdict = semver::version.compatible_with(beta5) ? "" : "in";
  printf("Compiled-in version %s is %scompatible with runtime version %s\n",
         semver::version.to_string().c_str(), verdict,
         beta5.to_string().c_str());

  verdict = semver::version.compatible_with(semver::get_version()) ? "" : "in";
  printf("Compiled-in version %s is %scompatible with runtime version %s\n",
         semver::version.to_string().c_str(), verdict,
         semver::get_version().to_string().c_str());

  verdict = beta5.compatible_with(rc) ? "" : "in";
  printf("Compiled-in version %s is %scompatible with runtime version %s\n",
         beta5.to_string().c_str(), verdict, rc.to_string().c_str());

  verdict = rc.compatible_with(beta5) ? "" : "in";
  printf("Compiled-in version %s is %scompatible with runtime version %s\n",
         rc.to_string().c_str(), verdict, beta5.to_string().c_str());
}
