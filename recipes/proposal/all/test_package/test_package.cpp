#include "PROPOSAL/PROPOSAL.h"
#include <iostream>
#include <memory>

int main()
{
    auto particle = PROPOSAL::MuMinusDef();
    auto target = PROPOSAL::Ice();
    auto cut = std::make_shared<PROPOSAL::EnergyCutSettings>(500, 0.05, false);
    auto cross = PROPOSAL::GetStdCrossSections(particle, target, cut, false);

    auto energy = 1e4;
    for (auto c : cross) {
        auto type = c->GetInteractionType();
        auto name = PROPOSAL::Type_Interaction_Name_Map.at(type);
        auto dEdx = c->CalculatedEdx(energy);
        std::cout << "The " << name << " average loss for a " << energy << " MeV "
                  << particle.name << " in " << target.GetName()
                  << " is: " << dEdx << " MeV * cm^2 / g" << std::endl;
    }
}
