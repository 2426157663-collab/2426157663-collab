function y = lab_1DLP(x,fs,fc)
% 输入：x 为时域信号，fs 为采样频率，fc 为截止频率。
% 输出：y 为滤波后的时域信号。
% 构造关于 0 Hz 对称的频率窗 H，完成 DFT->乘窗->IDFT。

N = length(x);
H = zeros(N,1);
df = fs/N;
tr = max(df,0.2*fc);

for i = 1:N
    f = (i-1)*df;
    d = min(f,fs-f);

    if d <= fc
        H(i) = 1;
    elseif d < fc+tr
        H(i) = (fc+tr-d)/tr;
    end
end

X = lab_DFT(x);
Y = X.*H;
y = lab_IDFT(Y);

if size(x,1)==1
    y = y.';
end
end
