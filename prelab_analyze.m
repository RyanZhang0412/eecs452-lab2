% EECS 452 Lab 2 Pre-Lab helper
% Place Canvas images in this folder (or edit the filenames below), then run:
%   >> prelab_analyze
%
% Works with Canvas names like:
%   fruit_min_light.jpg / fruit_mid_light.jpg / fruit_max_light.jpg
% (any *.jpg/*.png whose name contains min/mid/max)

clear; close all; clc;

files = dir('*.jpg');
if isempty(files), files = dir('*.png'); end
if isempty(files), files = dir('*.jpeg'); end
if isempty(files)
    error('No images found. Download min/mid/max light images from Canvas Lab 2 into this folder.');
end

names = {files.name};
minF = pick_file(names, {'min'});
midF = pick_file(names, {'mid'});
maxF = pick_file(names, {'max'});

fprintf('Using:\n  min: %s\n  mid: %s\n  max: %s\n', minF, midF, maxF);

Imin = im2double(imread(minF));
Imid = im2double(imread(midF));
Imax = im2double(imread(maxF));

HSVmin = rgb2hsv(Imin);
HSVmid = rgb2hsv(Imid);
HSVmax = rgb2hsv(Imax);

% ---- Q4: mid-light histograms ----
figure('Name','Q4 Mid-light RGB/HSV histograms');
chans = {'R','G','B','H','S','V'};
dataMid = {Imid(:,:,1), Imid(:,:,2), Imid(:,:,3), ...
           HSVmid(:,:,1), HSVmid(:,:,2), HSVmid(:,:,3)};
for k = 1:6
    subplot(2,3,k);
    imhist(dataMid{k});
    title(['Mid light: ' chans{k}]);
end

% ---- Q5/Q6: mean channel trends across lighting ----
meanRGB = [channel_means(Imin); channel_means(Imid); channel_means(Imax)];
meanHSV = [channel_means(HSVmin); channel_means(HSVmid); channel_means(HSVmax)];

figure('Name','Q5/Q6 Mean channel vs lighting');
subplot(1,2,1);
plot(1:3, meanRGB, '-o', 'LineWidth', 1.5); grid on;
xticks(1:3); xticklabels({'min','mid','max'});
ylabel('Mean intensity'); title('RGB means');
legend('R','G','B','Location','best');

subplot(1,2,2);
plot(1:3, meanHSV, '-o', 'LineWidth', 1.5); grid on;
xticks(1:3); xticklabels({'min','mid','max'});
ylabel('Mean value'); title('HSV means');
legend('H','S','V','Location','best');

fprintf('\nMean RGB [R G B]:\n');
disp(array2table(meanRGB, 'VariableNames',{'R','G','B'}, 'RowNames',{'min','mid','max'}));
fprintf('Mean HSV [H S V]:\n');
disp(array2table(meanHSV, 'VariableNames',{'H','S','V'}, 'RowNames',{'min','mid','max'}));

fprintf(['\nExpected trends:\n' ...
         '  RGB: R,G,B means rise from min->max\n' ...
         '  HSV: V rises; H relatively flat; S moderate change\n']);

function m = channel_means(I)
m = [mean(I(:,:,1),'all'), mean(I(:,:,2),'all'), mean(I(:,:,3),'all')];
end

function f = pick_file(names, keys)
for i = 1:numel(names)
    low = lower(names{i});
    for k = 1:numel(keys)
        if contains(low, keys{k})
            f = names{i};
            return;
        end
    end
end
error('Could not find an image whose name contains: %s', strjoin(keys, '/'));
end
