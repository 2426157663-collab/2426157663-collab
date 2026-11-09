function y = lab_lineconv(x1,x2)

N1 = length(x1);
N2 = length(x2);
y = zeros(1,N1+N2-1);

for i = 1:N1+N2-1
    for j = 1:N1
        k = i-j+1;

        if k>=1 && k<=N2
            y(i) = y(i)+x1(j)*x2(k);
        end
    end
end
end
