function y = lab_linecorr(x1,x2)

x2r = zeros(1,length(x2));
for i = 1:length(x2)
    x2r(i) = x2(length(x2)-i+1);
end

y = lab_lineconv(x1,x2r);
end
