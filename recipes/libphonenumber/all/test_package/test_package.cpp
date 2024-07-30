#include <phonenumbers/phonenumber.pb.h>
#include <phonenumbers/phonenumberutil.h>

int main() {
  using namespace i18n::phonenumbers;
  PhoneNumber number;
  number.set_country_code(1);
  number.set_national_number(uint64{650});
  auto util = PhoneNumberUtil::GetInstance();
  util->GetLengthOfGeographicalAreaCode(number);
}
