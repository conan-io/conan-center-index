// Include all headers to test they are where we expect and can be
// compiled.
#include <openassetio/errors.h>
#include <openassetio/BatchElementError.hpp>
#include <openassetio/Context.hpp>
#include <openassetio/EntityReference.hpp>
#include <openassetio/InfoDictionary.hpp>
#include <openassetio/TraitsData.hpp>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/hostApi/ManagerFactory.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/ConsoleLogger.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/log/SeverityFilter.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/managerApi/ManagerStateBase.hpp>
#include <openassetio/trait/TraitBase.hpp>
#include <openassetio/trait/collection.hpp>
#include <openassetio/trait/property.hpp>
#include <openassetio/typedefs.hpp>

int main() {
  auto traits = openassetio::TraitsData::make();
  traits->setTraitProperty("a", "b", openassetio::Str{"c"});
  return 0;
}
