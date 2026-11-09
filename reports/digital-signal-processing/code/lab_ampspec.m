function [f,A] = lab_ampspec(x,fs)
% 输入：x 为时域信号，fs 为采样频率。
% 输出：f 为 0~Nyquist 附近的频率坐标，A 为对应单边振幅。

N = length(x);
X = lab_DFT(x);
h = floor(N/2)+1;
f = (0:h-1)*fs/N;
A = zeros(1,h);

% 单边谱把负频率侧的幅值合并到正频率侧，因此一般乘以 2/N。
for k = 1:h
    A(k) = 2*abs(X(k))/N;
end

A(1) = A(1)/2;
end
