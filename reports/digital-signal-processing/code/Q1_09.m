% 功能：调用冲激、阶跃和矩形序列函数，构造四个组合离散序列。
% 思路：先生成各基本序列，再按照题目给出的系数进行逐点线性组合。

clear;
clc;
close all;

% x1(n)=delta(n-2)-2delta(n+5)
[d2,n] = lab_impulse(2,-10,10);
dm5 = lab_impulse(-5,-10,10);
x1 = d2 - 2*dm5;

% x2(n)=-u(n+10)+2u(n-3)
um10 = lab_jump(-10,-10,10);
u3 = lab_jump(3,-10,10);
x2 = -um10 + 2*u3;

% x3(n)=r11(n+5)-r5(n+2)
r11 = lab_rectangle(-5,11,-10,10);
r5 = lab_rectangle(-2,5,-10,10);
x3 = r11 - r5;

% x4(n)=u(n+10)-r3(n+5)-r3(n-3)
u0 = lab_jump(-10,-10,10);
rl = lab_rectangle(-5,3,-10,10);
rr = lab_rectangle(3,3,-10,10);
x4 = u0 - rl - rr;

figure;
stem(n,x1,'filled');
title('x1(n)=delta(n-2)-2delta(n+5)');
axis([-10,10,-3,3]);
grid on;

figure;
stem(n,x2,'filled');
title('x2(n)=-u(n+10)+2u(n-3)');
axis([-10,10,-3,3]);
grid on;

figure;
stem(n,x3,'filled');
title('x3(n)=r11(n+5)-r5(n+2)');
axis([-10,10,-3,3]);
grid on;

figure;
stem(n,x4,'filled');
title('x4(n)=u(n+10)-r3(n+5)-r3(n-3)');
axis([-10,10,-3,3]);
grid on;
