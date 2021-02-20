#include <stdexcept>
#include <iostream>
#include "TFile.h"
#include "TTree.h"
#include "TTreeReader.h"
#include "Event.hpp"


void check(bool result, std::string message) {
    if (!result) { throw std::runtime_error("ERROR : testrootdictionaries failed : " + message); }
}


void create_test_file(std::string name, const int Nevent, const int Npart) {
    auto tfile = TFile::Open(name.c_str(), "RECREATE");
    auto tree = new TTree("tree", "tree");
    Event* event = 0;
    tree->Branch("events", "Event", &event, 32000, 99);
    for(int eventnum = 0; eventnum < Nevent; ++eventnum) {
        event = new Event();
        for (int id = 0; id < Npart; ++id) {
            event->particles.push_back(Particle(id, {1.0, 2.0, 3.0, 4.0}));
        }
        tree->Fill();
        delete event;
        event = 0;
    }
    tree->Write();
    tfile->Close();
    delete tfile;
}


void read_test_file(std::string name, const int Nevent, const int Npart) {
    auto tfile = TFile::Open(name.c_str(), "READ");
    auto tree = tfile->Get<TTree>("tree");
    Event* event = 0;
    tree->SetBranchAddress("events", &event);
    check (tree->GetEntries() == Nevent, "event count mismatch");
    for(int eventnum = 0; eventnum < Nevent; ++eventnum) {
        check(tree->GetEntry(eventnum)>0, "read zero event size");
        check(event->particles.size() == Npart, "read no particles");
        for(int index = 0; index < Npart; ++index) {
            auto& p = event->particles.at(index);
            check(p.getID() == index, "read bad index");
            check(p.getP4().X() == 1.0, "read bad 4-vector");
        }
    }
}


int main() {
    std::cout << "--- testrootdictionaries " << std::endl;
    const std::string fname = "testevents.root";
    const int Nevent = 3;
    const int Npart = 3;
    create_test_file(fname, Nevent, Npart);
    read_test_file(fname, Nevent, Npart);
    std::cout << "--- testrootdictionaries... ok." << std::endl;
    return 0;
}


