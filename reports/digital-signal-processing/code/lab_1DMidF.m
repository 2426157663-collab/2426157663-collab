function y = lab_1DMidF(x,M)
% 对每个窗口中的样点排序并取中间值，能够有效抑制孤立尖峰和野值。
% 若边界处有效样点数为偶数，则取中间两个值的平均。

x = x(:).';
N = length(x);
r = floor(M/2);
y = zeros(1,N);

for i = 1:N
    data = zeros(1,M);
    c = 0;
    for j = i-r:i+r
        if j >= 1 && j <= N
            c = c+1;
            data(c) = x(j);
        end
    end
    data = sort(data(1:c));

    h = floor(c/2);
    if c == 2*h
        y(i) = (data(h)+data(h+1))/2;
    else
        y(i) = data(h+1);
    end
end
end
