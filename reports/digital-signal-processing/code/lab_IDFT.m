function xn = lab_IDFT(Xk)

N = length(Xk);
Xk = Xk(:);
xn = zeros(N,1);

for n = 0:N-1
    s = 0;
    for k = 0:N-1
        w = exp(1j*2*pi*k*n/N);
        s = s + Xk(k+1)*w;
    end

    % 理论上的实信号重建结果为实数；real 去除浮点运算产生的微小虚部。
    xn(n+1) = real(s)/N;
end
end
