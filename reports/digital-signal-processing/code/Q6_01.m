% 功能：针对五类一维噪声选择相应滤波方法，并以信噪比定量评价效果。
% 数据说明：signal 为无噪参考信号；n1~n5 依次为五种含噪信号。

close all;
clear;
clc;
load data_1D.mat;

fs = 1000;
N = length(signal);
t = (0:N-1)/fs;

% 1. 低频噪声：噪声集中在信号有效频带下方，使用高通滤波器抑制。
y1 = lab_1DHP(n1,fs,25);
showR(t,signal,n1,y1,fs, ...
           '低频噪声','results/10_低频噪声.png');

% 2. 高频噪声：有效信号主要位于低频，使用低通滤波器截除高频成分。
y2 = lab_1DLP(n2,fs,55);
showR(t,signal,n2,y2,fs, ...
           '高频噪声','results/11_高频噪声.png');

% 3. 随机噪声：先限制频带，再用 7 点均值滤波进一步平滑随机波动。
tmp = lab_1DLP(n3,fs,55);
y3 = lab_1DMF(tmp,7).';
showR(t,signal,n3,y3,fs, ...
           '随机噪声','results/12_随机噪声.png');

% 4. 野值噪声：孤立尖峰会显著偏离邻域，中值滤波对此类噪声较稳健。
y4 = lab_1DMidF(n4,5).';
showR(t,signal,n4,y4,fs, ...
           '野值噪声','results/13_野值噪声.png');

% 5. 工业电干扰：50 Hz 附近为窄带周期干扰，采用窄带带阻滤波器。
y5 = lab_1DBE(n5,fs,50,50.5);
showR(t,signal,n5,y5,fs, ...
           '工业电干扰','results/14_工业电干扰.png');

% 输出处理前后的 SNR，处理后数值越大表示误差功率越小。
fprintf('\n一维信号信噪比汇总（dB）\n');
fprintf('低频噪声：处理前 %.2f，处理后 %.2f\n', ...
        lab_snr(signal,n1),lab_snr(signal,y1));
fprintf('高频噪声：处理前 %.2f，处理后 %.2f\n', ...
        lab_snr(signal,n2),lab_snr(signal,y2));
fprintf('随机噪声：处理前 %.2f，处理后 %.2f\n', ...
        lab_snr(signal,n3),lab_snr(signal,y3));
fprintf('野值噪声：处理前 %.2f，处理后 %.2f\n', ...
        lab_snr(signal,n4),lab_snr(signal,y4));
fprintf('工业电干扰：处理前 %.2f，处理后 %.2f\n', ...
        lab_snr(signal,n5),lab_snr(signal,y5));

function showR(t,x0,xn,y,fs,name,pic)
% 统一绘制处理结果、振幅谱和相对参考信号的误差。

    [f,A] = lab_ampspec(y,fs);
    [p,b,e] = fileparts(pic);

    figure('Name',[name,'时域']);
    plot(t,y);
    grid on;
    title([name,'压制后的时间域信号']);
    xlabel('时间/s');
    ylabel('幅值');
    print(gcf,fullfile(p,[b,'_1_时域',e]),'-dpng','-r150');

    figure('Name',[name,'频谱']);
    plot(f,A);
    grid on;
    title('处理后信号的振幅谱');
    xlabel('频率/Hz');
    ylabel('振幅');
    print(gcf,fullfile(p,[b,'_2_频谱',e]),'-dpng','-r150');

    figure('Name',[name,'误差']);
    err = y-x0;
    plot(t,err);
    grid on;
    title(['处理误差，处理前SNR=',num2str(lab_snr(x0,xn),'%.2f'), ...
           ' dB，处理后SNR=',num2str(lab_snr(x0,y),'%.2f'),' dB']);
    xlabel('时间/s');
    ylabel('误差');
    print(gcf,fullfile(p,[b,'_3_误差',e]),'-dpng','-r150');
end
