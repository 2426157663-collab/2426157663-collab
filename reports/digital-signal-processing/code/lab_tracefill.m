function y = lab_tracefill(x,mis)
% 用相邻有效道插值恢复二维地震数据中的缺失道。
% 输入：x 为“采样点 x 道号”矩阵，mis 为缺失道号向量。
% 对内部缺道取左右最近有效道的平均；边界缺道复制唯一可用的一侧。

y = x;
[m,n] = size(x);

for k = 1:length(mis)
    j = mis(k);
    l = 0;
    r = 0;

    % 分别向左右搜索最近的有效道。
    for q = j-1:-1:1
        hit = 0;
        for p = 1:length(mis)
            if q == mis(p)
                hit = 1;
            end
        end
        if hit == 0
            l = q;
            break;
        end
    end

    for q = j+1:n
        hit = 0;
        for p = 1:length(mis)
            if q == mis(p)
                hit = 1;
            end
        end
        if hit == 0
            r = q;
            break;
        end
    end

    % 内部缺道取两侧平均，边界缺道复制可用的一侧。
    for i = 1:m
        if l > 0 && r > 0
            y(i,j) = (y(i,l)+y(i,r))/2;
        elseif l > 0
            y(i,j) = y(i,l);
        elseif r > 0
            y(i,j) = y(i,r);
        end
    end
end
end
