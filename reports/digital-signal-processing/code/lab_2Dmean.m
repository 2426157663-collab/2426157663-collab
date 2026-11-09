function y = lab_2Dmean(x,mt,mx)
% 输入：x 为 MxN 二维数据；mt、mx 分别为时间方向和空间方向窗口长度。
% 输出：y 与 x 尺寸相同，每一点取其二维邻域内有效样点的平均。
% 边界处仅统计实际存在的点，不进行补零。

[M,N] = size(x);
rt = floor(mt/2);
rx = floor(mx/2);
y = zeros(M,N);

for i = 1:M
    for j = 1:N
        s = 0;
        c = 0;

        for p = i-rt:i+rt
            for q = j-rx:j+rx
                if p >= 1 && p <= M && q >= 1 && q <= N
                    s = s + x(p,q);
                    c = c + 1;
                end
            end
        end
        y(i,j) = s/c;
    end
end
end
