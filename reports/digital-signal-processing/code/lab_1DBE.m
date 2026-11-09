function y = lab_1DBE(x,fs,f1,f2)
% f1~f2 为阻带，阻带外增益为 1；两个边界用线性镶边形成梯形窗。

N = length(x);
H = ones(N,1);
df = fs/N;
tr = max(df,0.1*(f2-f1));

for i = 1:N
    f = (i-1)*df;
    d = min(f,fs-f);

    if d >= f1 && d <= f2
        H(i) = 0;
    elseif d > f1-tr && d < f1
        H(i) = (f1-d)/tr;
    elseif d > f2 && d < f2+tr
        H(i) = (d-f2)/tr;
    end
end

X = lab_DFT(x);
Y = X.*H;
y = lab_IDFT(Y);

if size(x,1)==1
    y = y.';
end
end
