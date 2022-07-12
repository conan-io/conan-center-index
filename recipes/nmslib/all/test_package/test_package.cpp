#include "object.h"

#include <vector>
#include <string>


using namespace similarity;

int main(int argc, char* argv[]) {

    std::vector<string> strs = {
        "xyz", "beagcfa", "cea", "cb",
        "d", "c", "bdaf", "ddcd",
        "egbfa", "a", "fba", "bcccfe",
        "ab", "bfgbfdc", "bcbbgf", "bfbb"
    };

    for (int i = 0; i < 16; ++i) {
        LabelType label = i * 1000 + i;
        IdType    id = i + 1;
        Object* obj = new Object(id, label, strs[i].size(), strs[i].c_str());
        std::string tmp(obj->data(), obj->datalength());
        std::cout << tmp << std::endl;
        delete obj;
    }

    return 0;
};
