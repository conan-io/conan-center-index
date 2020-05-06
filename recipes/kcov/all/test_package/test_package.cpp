#include <cstdlib>
#include <iostream>
#include <ctime>
#include <string>


int main() {

    std::srand(std::time(nullptr)); // use current time as seed for random generator
    int random_variable = std::rand();
    std::string dir  = BUILD_DIR;

    if( random_variable %2 == 0){
        std::cout<<"branch1"<<std::endl;
    }else{
        std::cout<<"branch2"<<std::endl;
    }

    std::cout<<" *************************************************"<<std::endl;
    std::cout<<"open with you fav browser the coverage report at"  <<std::endl;
    std::cout<<dir<<"/cov/index.html"<<std::endl;
    std::cout<<" *************************************************"<<std::endl;

    return 0;

}
