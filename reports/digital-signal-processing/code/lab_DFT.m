function Xk = lab_DFT(xn)
% 输入：xn 为长度 N 的时域序列。
% 输出：Xk 为 N x 1 复数频谱列向量。

N = length(xn);
xn = xn(:);
Xk = zeros(N,1);

for k = 0:N-1
    s = 0;
    for n = 0:N-1
        w = exp(-1j*2*pi*k*n/N);
        s = s + xn(n+1)*w;
    end
    Xk(k+1) = s;
end
end
