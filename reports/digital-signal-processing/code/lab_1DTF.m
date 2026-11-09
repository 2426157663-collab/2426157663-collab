function y = lab_1DTF(x,M)
% 权值在窗口中心最大，向两侧按距离线性减小：

x = x(:).';
N = length(x);
r = floor(M/2);
y = zeros(1,N);

for i = 1:N
    s = 0;
    sw = 0;
    for j = -r:r
        p = i+j;
        if p >= 1 && p <= N
            w = r+1-abs(j);
            s = s + w*x(p);
            sw = sw + w;
        end
    end
    y(i) = s/sw;
end
end
