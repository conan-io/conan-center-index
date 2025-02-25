#include <xenium/nikolaev_queue.hpp>
#include <xenium/reclamation/generic_epoch_based.hpp>

int main(void) {
    xenium::nikolaev_queue<int, xenium::policy::reclaimer<xenium::reclamation::epoch_based<>>> queue;
  
    queue.push(0);
  
    int data = -1;
    queue.try_pop(data);

    return data;
}
