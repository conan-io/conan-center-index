#include <gtest/gtest.h>
#include <OptionsPricingModels/Option.hpp>
#include <OptionsPricingModels/BlackScholesModel.hpp>

TEST(BlackScholesModelTest, PriceCallOption) {
    double S0 = 100.0;
    double K = 100.0;
    double r = 0.05;
    double sigma = 0.2;
    double T = 1.0;

    OptionsPricingModels::Option callOption(K, T, OptionsPricingModels::OptionType::Call);
    OptionsPricingModels::BlackScholesModel bsModel;

    double price = bsModel.price(callOption, S0, r, sigma);
    double expectedPrice = 10.45;

    EXPECT_NEAR(price, expectedPrice, 0.1);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
