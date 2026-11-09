clear;
clc;
close all;

n = -25:0.01:25;
x = 2*sin(2*pi*n/20);

figure;
stem(n,x);
xlabel('n');
ylabel('x3(n)');
title('x3(n)=2*sin(2*pi*n/20)');
axis([-25,25,-3,3]);
grid on;
