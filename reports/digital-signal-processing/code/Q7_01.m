% 功能：对二维地震记录完成随机噪声压制、面波压制和缺道恢复。

close all;
clear;
clc;
load data_2D.mat;

% 1. 随机噪声压制
% 在“时间采样点-道号”二维邻域内取 3x3 均值，利用随机噪声均值趋近于零的特点。
y1 = lab_2Dmean(shot1,3,3);
showS(shotc,shot1,y1,'随机噪声压制', ...
         'results/15_二维随机噪声.png');

% 2. 面波压制
% 面波通常表现为强低频成分。逐道估计 21 点移动平均低频趋势，再从原道中相减。
[nt,nx] = size(shot2);
y2 = zeros(nt,nx);
for j = 1:nx
    lo = lab_1DMF(shot2(:,j),21);
    y2(:,j) = shot2(:,j)-lo.';
end
showS(shotc,shot2,y2,'面波压制', ...
         'results/16_面波压制.png');

% 3. 缺道恢复
% 若某一整道的绝对值和为 0，则判定该道缺失；随后进行相邻有效道插值。
mis = [];
for j = 1:size(shot3,2)
    if sum(abs(shot3(:,j))) == 0
        mis = [mis,j];
    end
end
y3 = lab_tracefill(shot3,mis);
showS(shotc,shot3,y3,'缺道恢复', ...
         'results/17_缺道恢复.png');

% 统一输出三项实验处理前后的信噪比。
fprintf('\n二维地震信号信噪比汇总（dB）\n');
fprintf('随机噪声：处理前 %.2f，处理后 %.2f\n', ...
        lab_snr(shotc,shot1),lab_snr(shotc,y1));
fprintf('面波干扰：处理前 %.2f，处理后 %.2f\n', ...
        lab_snr(shotc,shot2),lab_snr(shotc,y2));
fprintf('缺道数据：处理前 %.2f，处理后 %.2f\n', ...
        lab_snr(shotc,shot3),lab_snr(shotc,y3));

function showS(x0,xn,y,name,pic)
% 显示处理剖面、FK 谱和相对参考剖面的误差。

    % 自编二维 DFT 计算量较大，因此抽取部分时间点和道后再计算 FK 谱。
    sm = y(1:10:end,1:2:end);
    F = lab_DFT2(sm);

    % 把零频移到图像中心，并用对数压缩扩大弱频谱成分的可见范围。
    FK = log10(1 + abs(lab_shift2(F)));
    e = y-x0;

    c1 = max(abs(y(:)));
    c2 = max(abs(e(:)));
    [p,b,ex] = fileparts(pic);

    figure('Name',[name,'剖面']);
    imagesc(y);
    axis tight;
    colormap(jet(256));
    caxis([-c1,c1]);
    title([name,'后的时间域剖面']);
    xlabel('道号');
    ylabel('采样点');
    print(gcf,fullfile(p,[b,'_1_剖面',ex]),'-dpng','-r150');

    figure('Name',[name,'FK谱']);
    imagesc(FK);
    axis tight;
    colormap(hot(256));
    title('处理后二维振幅谱（FK谱）');
    xlabel('空间频率');
    ylabel('时间频率');
    print(gcf,fullfile(p,[b,'_2_FK谱',ex]),'-dpng','-r150');

    figure('Name',[name,'误差']);
    imagesc(e);
    axis tight;
    colormap(jet(256));
    caxis([-c2,c2]);
    title(['处理误差，SNR: ',num2str(lab_snr(x0,xn),'%.2f'), ...
           '→',num2str(lab_snr(x0,y),'%.2f'),' dB']);
    xlabel('道号');
    ylabel('采样点');
    print(gcf,fullfile(p,[b,'_3_误差',ex]),'-dpng','-r150');
end
