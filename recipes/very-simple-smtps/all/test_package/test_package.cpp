#include <cstdlib>
#include <iostream>
#include <algorithm>
#include <memory>
#include <sstream>
#include <string>

#include "very-simple-smtps/email.hpp"

using namespace smtp;

int main(void) {
  /*
   * Create a minimal usage for the target project here.
   * Avoid big examples, bigger than 100 lines.
   * Avoid networking connections.
   * Avoid background apps or servers.
   * The propose is testing the generated artifacts only.
   */

  EmailParams params{
      "user",                  // smtp username
      "password",              // smtp password
      "hostname",              // smtp server
      "bigboss@gmail.com",     // to
      "tully@gmail.com",       // from
      "All the bosses at PWC", // cc
      "PWC pay rise",          // subject
      "Hey mate, I have been working here for 5 years now, I think "
      "its time for a pay rise.", // body
  };

  Email email(params);

  std::stringstream ss;
  ss << email;
  const std::string &actual = ss.str();

  std::cout << actual << std::endl;
  return EXIT_SUCCESS;
}
