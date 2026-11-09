clear;
clc;
close all;

n = 0:0.01:50;
T = sqrt(228);
x = 2*sin(2*pi*n/T);

figure;
stem(n,x);
xlabel('n');
ylabel('x4(n)');
title('x4(n)=2*sin(2*pi*n/sqrt(228))');
axis([0,50,-3,3]);
grid on;
