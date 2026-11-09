function y = lab_1DGF(x,sg)
% sg 控制高斯权值的离散程度；窗口截取为 +/-3*sg，

x = x(:).';
N = length(x);
r = ceil(3*sg);
y = zeros(1,N);

for i = 1:N
    s = 0;
    sw = 0;
    for j = -r:r
        p = i+j;
        if p >= 1 && p <= N
            w = exp(-(j*j)/(2*sg*sg));
            s = s + w*x(p);
            sw = sw + w;
        end
    end
    y(i) = s/sw;
end
end
