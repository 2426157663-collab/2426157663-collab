clear;
clc;
close all;

n = 0:0.01:100;
T = 3.5^2.8;
a = 0.2*n;
c = sin(2*pi*n/T);
x = a.*c;

figure;
stem(n,x);
xlabel('n');
ylabel('x8(n)');
title('x8(n)=0.2*n.*sin(2*pi*n/3.5^2.8)');
axis([0,100,-20,20]);
grid on;
