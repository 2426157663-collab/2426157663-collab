function v = lab_snr(x0,y)

x0 = x0(:);
y = y(:);

Ps = 0;
Pn = 0;
for k = 1:length(x0)
    Ps = Ps + abs(x0(k))^2;
    Pn = Pn + abs(y(k)-x0(k))^2;
end

Ps = Ps/length(x0);
Pn = Pn/length(x0);

if Pn == 0
    v = inf;
else
    v = 10*log10(Ps/Pn);
    if abs(v) < 0.005
        v = 0;
    end
end
end
