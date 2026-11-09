function F = lab_DFT2(x)
%先对每一列做一维 DFT，再对中间结果的每一行做 DFT。

[M,N] = size(x);
temp = zeros(M,N);
F = zeros(M,N);

% 第一阶段：沿第 1 维（时间/行方向）对每一列变换。
for j = 1:N
    col = lab_DFT(x(:,j));
    temp(:,j) = col;
end

% 第二阶段：沿第 2 维（空间/列方向）对每一行变换。
for i = 1:M
    F(i,:) = lab_DFT(temp(i,:)).';
end
end
