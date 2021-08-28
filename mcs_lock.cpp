#include "mcs_lock.hpp"

thread_local MCSLock::MCSNode MCSLock::qnode;

void MCSLock::lock() {
  store_release(qnode.next, nullptr);
  MCSNode *pred = exchange(tail, &qnode);
  if (pred != nullptr) {
    store_release(qnode.locked, true);
    store_release(pred->next, &qnode);
    while (load_acquire(qnode.locked))
      ;
  }
}

void MCSLock::unlock() {
  MCSNode *succ = load_acquire(qnode.next);
  if (succ == nullptr) {
    auto expected = &qnode;
    if (compare_exchange(tail, expected, nullptr)) {
      return;
    }
    while (succ == nullptr) {
      succ = load_acquire(qnode.next);
    }
  }
  store_release(succ->locked, false);
}