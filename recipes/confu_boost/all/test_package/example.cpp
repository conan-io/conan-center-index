
#include "confu_boost/confuBoost.hxx"
#include <boost/archive/text_iarchive.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <iostream>
#include <sstream>
#include <string>

BOOST_FUSION_DEFINE_STRUCT((database), Character,
                           (std::string, id)(std::string,
                                             positionId)(std::string,
                                                         accountId))

BOOST_SERIALIZATION_BOILER_PLATE(database::Character)

int main() {
  auto characterStringStream = std::stringstream{};
  boost::archive::text_oarchive characterArchive{characterStringStream};
  characterArchive << database::Character{
      .id = "id", .positionId = "positionId", .accountId = "accountId"};
  assert(characterStringStream.str() ==
         "22 serialization::archive 19 0 0 2 id 10 positionId 9 accountId");
}
