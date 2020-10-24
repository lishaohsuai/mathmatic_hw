clear all;%%表示清空所有变量及变量值%%
%t=0:pi/360:2*pi;
%x=sin(t);
%y=cos(t);
%z=2*x.^2+y.^2;
t=xlsread('C:\Users\lee\Desktop\2p.xlsx');
tt = xlsread('C:\Users\lee\Desktop\2op.xlsx');
x = t(:,1);
y = t(:,2);
z = t(:,3);
xx = tt(:,1);
yy = tt(:,2);
zz = tt(:,3);

plot3(x,y,z,'Color','r','LineWidth',2);
hold on;
plot3(xx,yy,zz,'Color','g','LineWidth',2);
hold on;
%%三维曲线坐标轴和标题的设置%%
xlabel('x');
ylabel('y');
zlabel('z');
title('三维曲线图');

%axis([-1.2 1.2 -1.2 1.2 0.5 2.2])
