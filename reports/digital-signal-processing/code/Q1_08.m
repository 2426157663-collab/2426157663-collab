clear;
clc;
close all;

n = 0:0.01:100;
a = 2 + 50./(n+1);
p = 2*pi*n./(0.2*n+1.5^2.8);
x = a.*sin(p);

figure;
stem(n,x);
xlabel('n');
ylabel('x10(n)');
title('x10(n)=(2+50./(n+1)).*sin(2*pi*n./(0.2*n+1.5^2.8))');
axis([0,100,-30,30]);
grid on;
