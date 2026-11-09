clear;
clc;
close all;

n = 0:0.01:50;
T = sqrt(228);
p = -pi/2;
x = 2*cos(2*pi*n/T + p);

figure;
stem(n,x);
xlabel('n');
ylabel('x5(n)');
title('x5(n)=2*cos(2*pi*n/sqrt(228)-pi/2)');
axis([0,50,-3,3]);
grid on;
