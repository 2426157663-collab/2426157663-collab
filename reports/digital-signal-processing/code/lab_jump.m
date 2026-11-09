function [x,n] = lab_jump(n0,n1,n2)

n = n1:n2;
x = zeros(1,length(n));

for i = 1:length(n)
    if n(i) >= n0
        x(i) = 1;
    else
        x(i) = 0;
    end
end
end
