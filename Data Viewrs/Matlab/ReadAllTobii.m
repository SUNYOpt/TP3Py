clear all
close all
%% Subject name and the directory of the data meant for processing
% Inputs
Sub = '202208091801';
filedir = ['C:\Users\hrahi\Desktop\TP3Py\hrn\', Sub,'\']; % the folder that contrains the data 
addpath('quaternion_library');      % include quaternion library


% Parameters
YlimET = [0 1]; % eye movements y limits
YlimETangle = [-15 15]; % eye movements y limits
YlimHead = [-45 70];
YlimConv = [0 30];    % convergence y limits
PupilYLim = [2.5 5.5];% pupil y limits
AveConvLim = [0 1500];
TimingLim = [-0.05 0.05];
TimeWindow = 8;
TPup = 0:1/40:TimeWindow;
TZ =  0:1/40:TimeWindow;
% Outputs
PupilMedians= []; % a matrix of medain pupil measurements of left and right eyes (rows) and measurements (columns)
Convergence = []; % a matrix of medain convergence measurements of horizontal and vertical vergence (rows) and measurements (columns)
Zvalue            = []; % a Vector of medain gaze plane distance (Z) measurements (columns)

% Visuals 
myfig = figure();
set(gcf, 'Position', get(0, 'Screensize'));



%% Finding Tobii's data - including eye tracking, timings, and IMU signals
textFiles = dir([filedir, '*.txt']);

for t = 1:numel(textFiles)
    namestring = textFiles(t).name;
    
    if strcmp(namestring(1:8) , 'Gazedata')
        GazeInds = t;
    elseif  strcmp(namestring(1:6) , 'TSdata')
        TSInd = t;
    elseif strcmp(namestring(1:7) , 'IMUdata')
        IMInd = t;
    end
end

temp = textFiles(GazeInds).name;
FileName = temp(10:end-4);

% importing the gaze data
A = importdata([filedir, textFiles(GazeInds).name]);                          
F(length(A)) = struct('tgz',[]);
for i = 1:length(A)
    gp3 = (cell2mat(A(i)));
    tempS = jsondecode(gp3);
    fnames = fieldnames(tempS) ;
    for ff = 1:numel(fnames)
        F(i).(cell2mat(fnames(ff))) = tempS.(cell2mat(fnames(ff)));
    end
end

% importing the TS data
ATime = importdata([filedir, textFiles(TSInd).name]);                       
FTime(length(ATime)) = struct('tgz',[]);
for i = 1:length(ATime)
    gp3 = (cell2mat(ATime(i)));
    tempS = jsondecode(gp3);
    fnames = fieldnames(tempS) ;
    for ff = 1:numel(fnames)
        FTime(i).(cell2mat(fnames(ff))) = tempS.(cell2mat(fnames(ff)));
    end
end

% importing the IMU data
AIMU= importdata([filedir, textFiles(IMInd).name]);                       
FIMU(length(AIMU)) = struct('tacc',[]);
for i = 1:length(AIMU)
    gp3 = (cell2mat(AIMU(i)));
    tempS = jsondecode(gp3);
    fnames = fieldnames(tempS) ;
    for ff = 1:numel(fnames)
        FIMU(i).(cell2mat(fnames(ff))) = tempS.(cell2mat(fnames(ff)));
    end
end

%% Data Extraction from structures
t = [F.tgz] ;
Gaze = [F.gaze2d];
Gaze3D = [F.gaze3d];


tTTL = [t(1) t(end)+2];

tgzp = t;

% Extracting pupil data and measuring convergence
iL = 1;
iR = 1;
iConv = 1;
RightP = []; TimeRP = []; LeftP = []; TimeLP = [];
hConv = []; vConv = []; TimeConv = []; PupDist = [];
LeftH = []; RightH = [];
for i = 1:numel(F)
    if isfield(F(i).eyeright,'pupildiameter')
        RightP(iR) = [F(i).eyeright.pupildiameter];
        TimeRP(iR) =tgzp(i);
        iR = iR+1;
    end
    if isfield(F(i).eyeleft,'pupildiameter')
        LeftP(iL) = [F(i).eyeleft.pupildiameter];
        TimeLP(iL) =tgzp(i);
        iL = iL+1;
    end

    if isfield(F(i).eyeleft,'gazedirection') & isfield(F(i).eyeright,'gazedirection') 
        LeftDir =  [F(i).eyeleft.gazedirection];
        RighDir = [F(i).eyeright.gazedirection];
        
        LeftOrig =  [F(i).eyeleft.gazeorigin];
        RighOrig = [F(i).eyeright.gazeorigin];
        PupDist(iConv,:) = LeftOrig-RighOrig;
        hConv(iConv) = abs(atan(LeftDir(1)/LeftDir(3)) - atan(RighDir(1)/RighDir(3)))* 180/pi;
        
        hConv(iConv) = abs(acos(LeftDir(1)*RighDir(1) + LeftDir(2)*RighDir(2) +LeftDir(3)*RighDir(3)  )) * 180/pi;
        
        vConv(iConv)= abs(atan(LeftDir(2)/LeftDir(3)) - atan(RighDir(2)/RighDir(3)))* 180/pi;
        TimeConv(iConv) =tgzp(i);
        
        LeftH(iConv) = atan(LeftDir(1)/LeftDir(3))*180/pi;
        RightH(iConv) = atan(RighDir(1)/RighDir(3))*180/pi;
       
        iConv = iConv+1;
    end
end
medPL = median(LeftP);
medPR = median(RightP);

% Finding start 's' and end 'e' keyboard triggers for sectioning data
% keyTriggers = find(cellfun(@(x) ~isempty(x), {FTime.KeyEvents}));
% KeyTimes = [FTime(keyTriggers).tevent];
% StartTriggers = find(cellfun(@(x) contains(x,'s'), {FTime(keyTriggers).KeyEvents}));
% EndTriggers = find(cellfun(@(x) contains(x,'e'), {FTime(keyTriggers).KeyEvents}));

% Finding the TTLs start and end
% ttlTriggers = find(cellfun(@(x) ~isempty(x), {FTime.tttl}));
% TTLtimes = [FTime(ttlTriggers).tttl];
% StartTTLs = find(cellfun(@(x) x == 1, {FTime(ttlTriggers).value}));
% EndTTLs= find(cellfun(@(x) x == 0, {FTime(ttlTriggers).value}));


%% 
figure(myfig)

subplot(6,2,[1 2])

h1= plot(t, Gaze(1,:), 'b'); hold on;
h2 = plot(t, Gaze(2,:), 'r');


xlim([tTTL(1) tTTL(2)+2])
ylim(YlimET)
ylabel('Gaze 2D')
set(gca,'xtick',[])

%gcat =gca; gcat.XAxis.Visible = 'off';
set(gca,'tickdir','out')
set(gca, 'linewidth', 2)
set(gca, 'fontsize', 9)
box off

%% Plotting 2D gaze direction 
subplot(6,2,[3 4])

h1= plot(TimeConv, LeftH, 'b'); hold on;
h2 = plot(TimeConv, RightH, 'r');

xlim([tTTL(1) tTTL(2)+2])
ylim(YlimETangle)
ylabel('Horizontal Gaze angle')
set(gca,'xtick',[])
legend([h1,h2], {'Left eye', 'Right eye'})

gcat =gca; gcat.XAxis.Visible = 'off';
set(gca,'tickdir','out')
set(gca, 'linewidth', 2)
set(gca, 'fontsize', 9)
box off

%% Plotting pupil size of right and left eyes
subplot(6,2,[5 6])
h1= plot(TimeLP, LeftP, 'b'); hold on;
h2 = plot(TimeRP, RightP, 'r');
xlim([tTTL(1) tTTL(2)+2])


ylim(PupilYLim)
ylabel('Pupil Diam.')
set(gca,'xtick',[])
legend([h1,h2], {'Left eye', 'Right eye'})

gcat =gca; gcat.XAxis.Visible = 'off';
set(gca,'tickdir','out')
set(gca, 'linewidth', 2)
set(gca, 'fontsize', 9)
box off

%% convergence
subplot(6,2,[7 8])

h1= plot(TimeConv, hConv, 'b'); hold on;
h2 = plot(TimeConv, vConv, 'r');
xlim([tTTL(1) tTTL(2)+2])


ylim(YlimConv)
ylabel('Vergence')
set(gca,'xtick',[])
legend([h1,h2], {'Horizontal', 'Right eye'})
gcat =gca; gcat.XAxis.Visible = 'off';
set(gca,'tickdir','out')
set(gca, 'linewidth', 2)
set(gca, 'fontsize', 9)
box off

%% heading
subplot(6,2,[9 10])

[ttime, euler] = getHeading_GUO(FIMU)
h1= plot(ttime, euler(:, 1)-90, 'r'); hold on;
h2 = plot(ttime, euler(:, 2), 'g');
h3 = plot(ttime, euler(:, 3), 'b');

xlim([tTTL(1) tTTL(2)+2])

ylim(YlimHead)
ylabel('Vergence')
set(gca,'xtick',[])

gcat =gca; gcat.XAxis.Visible = 'off';
set(gca,'tickdir','out')
set(gca, 'linewidth', 2)
set(gca, 'fontsize', 9)
box off

xlabel('time (s)');


%% Tining
subplot(6,2,[11 12])
tacc = [FIMU.tacc];
tSceneM = [FTime.ttsscene];
teyeM = [FTime.ttseye];

h1= plot(t(1:end-1), diff(t), 'b');  hold on;
h2 = plot(tacc(1:end-1), diff(tacc),  'r');
h3 = plot(tSceneM(1:end-1), diff(tSceneM), 'g');
h4 = plot(teyeM(1:end-1), diff(teyeM), 'k');

xlim([tTTL(1) tTTL(2)+2])


ylim(TimingLim)
ylabel('Vergence')
legend([h1,h2, h3, h4], {'gaze', 'acc',  'SM', 'EM'})

set(gca,'tickdir','out')
set(gca, 'linewidth', 2)
set(gca, 'fontsize', 9)
box off

xlabel('time (s)');


difftosee = diff(teyeM(2:end));
missrate = sum(difftosee(difftosee > 1.5*1/50))/sum((difftosee>0));

%% Correlations
[R,P] = corrcoef(interp1(TimeConv,LeftH, ttime), euler(:, 3)') ;
[R,P] = corrcoef(interp1(TimeConv,(RightH+LeftH)/2, ttime), euler(:, 3)') ;
[r,lags] = xcorr(interp1(TimeConv,(RightH+LeftH)/2, ttime), euler(:, 3)');

% Saving analysis figure 
saveas(myfig, [Sub, '.jpg'])