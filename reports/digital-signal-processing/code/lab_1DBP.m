function y = lab_1DBP(x,fs,f1,f2)
% f1~f2 为通带；两侧设置线性过渡区，区外频率增益为 0。
% d=min(f,fs-f) 用于把 DFT 后半段映射为对应的负频率绝对值，
% 从而保证实信号滤波器具有共轭对称的频率响应。

N = length(x);
H = zeros(N,1);
df = fs/N;
tr = max(df,0.1*(f2-f1));

for i = 1:N
    f = (i-1)*df;
    d = min(f,fs-f);

    if d >= f1 && d <= f2
        H(i) = 1;
    elseif d > f1-tr && d < f1
        H(i) = (d-f1+tr)/tr;
    elseif d > f2 && d < f2+tr
        H(i) = (f2+tr-d)/tr;
    end
end

X = lab_DFT(x);
Y = X.*H;
y = lab_IDFT(Y);

if size(x,1)==1
    y = y.';
end
end
