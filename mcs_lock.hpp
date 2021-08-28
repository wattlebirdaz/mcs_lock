#pragma once

#include "atomic_wrapper.hpp"

struct MCSLock {
  struct MCSNode {
    MCSNode *next;
    bool locked;
  };

  MCSNode *tail = nullptr;
  static thread_local MCSNode qnode;

  void lock();

  void unlock();
};
