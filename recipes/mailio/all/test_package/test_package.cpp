#include <mailio/message.hpp>
#include <mailio/smtp.hpp>
#include <iostream>

int main() {
  mailio::message msg;
  msg.from(mailio::mail_address("mailio library", "mailio@gmail.com"));
  msg.add_recipient(mailio::mail_address("mailio library", "mailio@gmail.com"));
  msg.subject("smtps simple message");
  msg.content("Hello, World!");

  mailio::smtps conn("smtp.gmail.com", 587);
  std::cout << msg.content() << "\n";;
}
