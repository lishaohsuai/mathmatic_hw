clear all;%%��ʾ������б���������ֵ%%
%t=0:pi/360:2*pi;
%x=sin(t);
%y=cos(t);
%z=2*x.^2+y.^2;
t=xlsread('C:\Users\lee\Desktop\2p.xlsx');

x = t(:,1);
y = t(:,2);
z = t(:,3);

plot3(x,y,z,'Color','r','LineWidth',2);
%%��ά����������ͱ��������%%
xlabel('x');
ylabel('y');
zlabel('z');
title('��ά����ͼ');

%axis([-1.2 1.2 -1.2 1.2 0.5 2.2])
