#include <cstdlib>
#include <iostream>
#include <algorithm>
#include <memory>
#include <sstream>
#include <string>

#include "date_time_now.hpp"
#include "email/email.hpp"
#include "mime/mime.hpp"

using namespace smtp;

int main(void) {
  /*
    * Create a minimal usage for the target project here.
    * Avoid big examples, bigger than 100 lines.
    * Avoid networking connections.
    * Avoid background apps or servers.
    * The propose is testing the generated artifacts only.
    */

  const auto dateTimeStatic = std::make_unique<DateTimeStatic>();

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
      dateTimeStatic.get()        // optional datetime
  };

  Email email(params);

  const std::string &expected =
      "To: bigboss@gmail.com\r\n"
      "From: tully@gmail.com\r\n"
      "Cc: All the bosses at PWC\r\n"
      "Subject: PWC pay rise\r\n"
      "25/07/2023 07:21:05 +1100\r\n"
      "User-Agent: Very-Simple-SMTPS\r\n"
      "MIME-Version: 1.0\r\n"
      "Content-Type: multipart/mixed;\r\n"
      " boundary=\"----------030203080101020302070708\"\r\n"
      "\r\n"
      "This is a multi-part message in MIME format.\r\n"
      "------------030203080101020302070708\r\n"
      "Content-Type: text/plain; charset=utf-8; format=flowed\r\n"
      "Content-Transfer-Encoding: 7bit\r\n"
      "\r\n"
      "Hey mate, I have been working here for 5 years now, I think its time for a pay rise.\r\n"
      "------------030203080101020302070708\r\n"
      "------------030203080101020302070708--\r\n"
      ".\r\n";

  std::stringstream ss;
  ss << email;
  const std::string &actual = ss.str();
  

  return expected == actual ? EXIT_SUCCESS : EXIT_FAILURE;
}
