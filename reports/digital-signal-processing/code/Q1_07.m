clear;
clc;
close all;

n = 0:0.01:100;
d = 0.2*n + 1.5^2.8;
p = 2*pi*n./d;
x = 2*sin(p);

figure;
stem(n,x);
xlabel('n');
ylabel('x9(n)');
title('x9(n)=2*sin(2*pi*n./(0.2*n+1.5^2.8))');
axis([0,100,-3,3]);
grid on;
