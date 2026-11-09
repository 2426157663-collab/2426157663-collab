function [x,n] = lab_impulse(n0,n1,n2)
% 输入：n0 为冲激位置；n1、n2 为输出序列的起止下标。
% 输出：x 为冲激序列，n 为对应的离散下标。

n = n1:n2;
x = zeros(1,length(n));

for i = 1:length(n)
    if n(i) == n0
        x(i) = 1;
    else
        x(i) = 0;
    end
end
end
