function y = lab_shift2(x)

[M,N] = size(x);
y = zeros(M,N);
rm = floor(M/2);
rn = floor(N/2);

for i = 1:M
    for j = 1:N
        ii = i-1+rm;
        if ii >= M
            ii = ii-M;
        end

        jj = j-1+rn;
        if jj >= N
            jj = jj-N;
        end

        y(i,j) = x(ii+1,jj+1);
    end
end
end
