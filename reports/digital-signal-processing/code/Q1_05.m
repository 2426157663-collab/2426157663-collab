% 思路：先计算常量周期参数，再把整个 n 向量代入正弦表达式。

clear;
clc;
close all;

n = 0:0.01:50;
T = 3.5^2.8;
x = 2*sin(2*pi*n/T);

figure;
stem(n,x);
xlabel('n');
ylabel('x7(n)');
title('x7(n)=2*sin(2*pi*n/3.5^2.8)');
axis([0,50,-3,3]);
grid on;
