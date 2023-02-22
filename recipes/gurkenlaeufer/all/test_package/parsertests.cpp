#include "gmock/gmock.h"
#include "gtest/gtest.h"

#include "gurkenlaeufer/Parser.h"
#include "gurkenlaeufer/ParserStateFactory.h"
#include "gurkenlaeufer/ScenarioCollection.h"
#include "gurkenlaeufer/ScenarioInterface.h"

using namespace testing;
using namespace gurkenlaeufer;

struct MockIScenarioCollection : public IScenarioCollection {
    MOCK_METHOD1(appendScenario, void(Scenario steps));
    MOCK_CONST_METHOD0(getScenarios, std::list<Scenario>());
};

TEST(ParserTest, shouldParseOneScenario)
{
    auto scenariosMock = std::make_shared<MockIScenarioCollection>();
    Parser parser(IParserStateFactoryPtr(new ParserStateFactory(scenariosMock)));

    EXPECT_CALL(*scenariosMock, appendScenario(_));
    parser.parseLine("Scenario: Add two numbers.");
    parser.parseLine("Given I have entered 1 into the calculator");
    parser.finish();
}

