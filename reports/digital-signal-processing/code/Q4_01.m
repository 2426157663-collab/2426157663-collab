% 功能：构造含 10 Hz、60 Hz、200 Hz 三个分量的信号，测试四类频域滤波器。
% 方法：DFT -> 与梯形频率窗逐点相乘 -> IDFT。

clear;
clc;
close all;

fs = 1000;
T = 0.5;
t = 0:1/fs:T-1/fs;

% 三个频率分量的幅值分别为 1、0.7、0.5。
x = sin(2*pi*10*t) + 0.7*sin(2*pi*60*t) + 0.5*sin(2*pi*200*t);

lp = lab_1DLP(x,fs,20);
hp = lab_1DHP(x,fs,100);
bp = lab_1DBP(x,fs,40,80);
be = lab_1DBE(x,fs,40,80);

figure;
plot(t,x);
title('原始信号');
xlabel('时间/s');
grid on;

figure;
plot(t,lp);
title('低通滤波：保留低频分量');
xlabel('时间/s');
grid on;

figure;
plot(t,hp);
title('高通滤波：保留高频分量');
xlabel('时间/s');
grid on;

figure;
plot(t,bp);
title('带通滤波：保留中间频带');
xlabel('时间/s');
grid on;

figure;
plot(t,be);
title('带阻滤波：抑制中间频带');
xlabel('时间/s');
grid on;
