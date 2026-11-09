function y = lab_circorr(x1,x2,N)
x1n = zeros(1,N);
x2n = zeros(1,N);
y = zeros(1,N);

for i = 1:N
    if i <= length(x1)
        x1n(i) = x1(i);
    end
    if i <= length(x2)
        x2n(i) = x2(i);
    end
end

for m = 0:N-1
    for i = 0:N-1
        j = i-m;

        if j < 0
            j = j+N;
        end
        y(m+1) = y(m+1)+x1n(i+1)*x2n(j+1);
    end
end
end
