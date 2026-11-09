% 功能：调用自编 DFT/IDFT，观察双频信号的频谱并验证可逆性。
% 信号包含归一化频率为 3/32 和 7/32 的两个正弦分量。

clear;
clc;
close all;

N = 32;
n = 0:N-1;
x = sin(2*pi*3*n/N) + 0.5*sin(2*pi*7*n/N);

X = lab_DFT(x);
y = lab_IDFT(X);

figure;
stem(0:N-1,abs(X));
title('DFT振幅谱');
xlabel('频率序号 k');
ylabel('|X(k)|');
grid on;

figure;
plot(n,x,'o-');
hold on;
plot(n,y,'x--');
title('IDFT重建结果');
xlabel('n');
ylabel('幅值');
legend('原信号','重建信号');
grid on;
