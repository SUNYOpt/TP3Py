function [ttime, euler] = getHeading_GUO(FIMU)

time = [FIMU.tacc] ;
tmag = [FIMU.tmag];
Magn = [FIMU.magnetometer];
Gyro = [FIMU.gyroscope];
Acc = [FIMU.accelerometer];
ttime = time(time>tmag(1) & time<tmag(end));
Gyro = Gyro(:, time>tmag(1) &time<tmag(end));
Acc    =  Acc(:, time>tmag(1) &time<tmag(end))';


MgX = Magn(1,:);
MgY = Magn(2,:);
MgZ = Magn(3,:);
% loading the Callibration for magnetometer
load('magCal.mat')
MgXc = (MgX-MgXoff)*MgXgain;
MgYc = (MgY-MgYoff)*MgYgain;
MgZc = (MgZ-MgZoff)*MgZgain;


MagInteX = interp1(tmag, MgXc, ttime);
MagInteY = interp1(tmag, MgYc, ttime);
MagInteZ = interp1(tmag, MgZc, ttime);
Magnetometer = [MagInteX', MagInteY', MagInteZ'];

% loading the Callibration for gyro/acc
load('GyroCal.mat')
Gyroc = Gyro - GyroOffset;
Gyroc = Gyroc';
qin1  =[1,0,0,0];

[quaternion] = GUO([zeros(size(Acc,1),1), Acc(:,[1 2 3]),Gyroc(:,[1 2 3])* (pi/180),[MagInteX', MagInteY',MagInteZ']], ...
    [GyroVar]* (pi/180), AccVar, ...
    MagVar, qin1)
euler = quatern2euler(quaternConj(quaternion)) * (180/pi);	% use conjugate for sensor frame relative to Earth and convert to degrees.

