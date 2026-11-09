% 功能：数值验证两个重要性质：
% 1) 当 N>=N1+N2-1 时，补零后的 N 点循环褶积等于线性褶积；
% 2) 对实序列，线性相关等于“第二序列反序后”与第一序列的线性褶积。

clear;
clc;
close all;

x1 = [1,2,3,2];
x2 = [2,-1,1];
N = length(x1)+length(x2)-1;

lc = lab_lineconv(x1,x2);
cc = lab_circonv(x1,x2,N);

x2r = zeros(1,length(x2));
for i = 1:length(x2)
    x2r(i) = x2(length(x2)-i+1);
end
lr = lab_linecorr(x1,x2);
rc = lab_lineconv(x1,x2r);

figure;
plot(lc,'o-');
hold on;
plot(cc,'x--');
title('线性褶积与循环褶积对比');
legend('线性褶积','循环褶积');
grid on;

figure;
plot(lr,'o-');
hold on;
plot(rc,'x--');
title('线性相关与线性褶积对比');
legend('线性相关','反序后线性褶积');
grid on;
