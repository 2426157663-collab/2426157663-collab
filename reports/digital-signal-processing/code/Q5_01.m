% 功能：比较均值、三角、高斯和中值四种一维时域滤波方法。
% 对比重点：前三种属于加权平滑，中值滤波属于非线性排序统计滤波。

close all;
clear;
clc;

N = 200;
n = 0:N-1;
x0 = sin(2*pi*0.05*n) + 0.4*sin(2*pi*0.13*n);

rng(2);
xn = x0 + 0.6*randn(1,N);

ym = lab_1DMF(xn,5);
yt = lab_1DTF(xn,5);
yg = lab_1DGF(xn,1.0);
yd = lab_1DMidF(xn,5);

figure('Name','无噪信号');
plot(x0);
grid on;
title('无噪信号');
print(gcf,'results/09_时域滤波_1_无噪信号.png','-dpng','-r150');

figure('Name','含噪信号');
plot(xn);
grid on;
title('含噪信号');
print(gcf,'results/09_时域滤波_2_含噪信号.png','-dpng','-r150');

figure('Name','均值滤波');
plot(ym);
grid on;
title('均值滤波');
print(gcf,'results/09_时域滤波_3_均值滤波.png','-dpng','-r150');

figure('Name','三角滤波');
plot(yt);
grid on;
title('三角滤波');
print(gcf,'results/09_时域滤波_4_三角滤波.png','-dpng','-r150');

figure('Name','高斯滤波');
plot(yg);
grid on;
title('高斯滤波');
print(gcf,'results/09_时域滤波_5_高斯滤波.png','-dpng','-r150');

figure('Name','中值滤波');
plot(yd);
grid on;
title('中值滤波');
print(gcf,'results/09_时域滤波_6_中值滤波.png','-dpng','-r150');
