function y = lab_1DHP(x,fs,fc)
% 低于 fc 的频率被抑制，高于 fc 的频率被保留；
% 截止频率下方设置线性过渡带，以减小矩形窗突变造成的时域振铃。

N = length(x);
H = zeros(N,1);
df = fs/N;
tr = max(df,0.2*fc);

for i = 1:N
    f = (i-1)*df;
    d = min(f,fs-f);

    if d >= fc
        H(i) = 1;
    elseif d > fc-tr
        H(i) = (d-fc+tr)/tr;
    end
end

X = lab_DFT(x);
Y = X.*H;
y = lab_IDFT(Y);

if size(x,1)==1
    y = y.';
end
end
