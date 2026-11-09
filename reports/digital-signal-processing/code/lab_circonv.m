function y = lab_circonv(x1,x2,N)
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

for i = 0:N-1
    for j = 0:N-1
        k = i-j;

        if k < 0
            k = k+N;
        end
        y(i+1) = y(i+1)+x1n(j+1)*x2n(k+1);
    end
end
end
