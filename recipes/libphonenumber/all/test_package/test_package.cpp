#include <phonenumbers/phonenumber.pb.h>
#include <phonenumbers/phonenumbermatch.h>

int main() {
  using namespace i18n::phonenumbers;
  PhoneNumber number;
  const int start_index = 10;
  const string raw_phone_number("1 800 234 45 67");
  PhoneNumberMatch match(start_index, raw_phone_number, number);
}
