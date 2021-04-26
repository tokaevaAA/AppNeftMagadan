#pragma once

#include <iostream>

class A {
public:
    A();
    template<class T> void print(T);  
};

A::A() {}

template<> void A::print(int x) { std::cout << x << std::endl;}
