% 功能：调用自编函数，分别完成线性/循环褶积和线性/循环相关。
% 数据：magic(100) 的不同行作为测试序列；减去列均值以削弱直流分量。

close all;
clear;
clc;

raw = magic(100);
x = raw - mean(raw);

% 1. 线性褶积：长度应为 100+100-1=199。
y1 = lab_lineconv(x(1,:),x(2,:));
figure;
plot(y1);
title('线性褶积结果');
xlabel('输出样点');
ylabel('幅值');
grid on;

% 2. 110 点循环褶积：两个输入先补零或截取到指定循环长度。
y2 = lab_circonv(x(3,:),x(4,:),110);
figure;
plot(y2);
title('循环褶积结果');
xlabel('循环移位量');
ylabel('幅值');
grid on;

% 3. 线性相关：第二个序列平方后与第一个序列进行滑动相似性度量。
y3 = lab_linecorr(x(5,:),x(6,:).^2);
figure;
plot(y3);
title('线性相关结果');
xlabel('相对位移');
ylabel('相关值');
grid on;

% 4. 110 点循环相关：序列按长度 110 周期延拓后计算相关。
y4 = lab_circorr(x(7,:).^2,x(8,:),110);
figure;
plot(y4);
title('循环相关结果');
xlabel('循环位移量');
ylabel('相关值');
grid on;
