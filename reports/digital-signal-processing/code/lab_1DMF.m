function y = lab_1DMF(x,M)
% 输入：x 为待滤波序列，M 为窗口长度。
% 每个输出点等于其邻域内有效样点的算术平均值。

x = x(:).';
N = length(x);
r = floor(M/2);
y = zeros(1,N);

for i = 1:N
    s = 0;
    c = 0;
    for j = i-r:i+r
        if j >= 1 && j <= N
            s = s + x(j);
            c = c + 1;
        end
    end
    y(i) = s/c;
end
end
