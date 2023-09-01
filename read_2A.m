clear
clc

% str为绝对路径，最外层循环读取每一批数据中的所有文件,并处理
str1 = '/Users/zhiyuzhang/MyProjects/csimGPR/examples/';
m = 11;

% str=strcat(str1,str2,'\HH');%绝对路径文件名
files=dir(fullfile(str1,'*.2B'));%更改2B或2C
filescells=struct2cell(files);


%% 数据读取 DS1存放所有数据，DS2存放E2为位置信息
precision1= 'unsigned char';%科学数据内容标识
skip1=16452;
precision2= 'unsigned char';%高频天线极化
skip2=16452;
precision3= 'uint16';%科学数据有效长度
skip3=16451;
precision4= '4096*single';%科学数据
skip4=69;
precision5= '3*single';%位置信息
skip5=16441;

A=[];A1=[];B=[];B1=[];C=[];C1=[]; D=[];D01=[]; D1=[];D1=[];E=[];E1=[]; E2=[];

% xiangduilujing = './examples/HX1-Ro_GRAS_RoPeR-HF-HH_SCI_N_20210525042001_20210525043243_00011_A.2B';

for i=1:size(filescells,2)
    c=char(filescells(1,i));
    d=char(filescells(2,i));
    xiangduilujing=strcat(d,'/',c);
    disp(xiangduilujing)

    fid=fopen(xiangduilujing,'r');
    fseek(fid,11,'bof');
    A=fread(fid,inf,precision1,skip1);
    A=A.';
    A1=[A1,A];
    fseek(fid,14,'bof');
    B=fread(fid,inf,precision2,skip2);
    B=B.';
    B1=[B1,B];
    fseek(fid,16,'bof');
    C=fread(fid,inf,precision3,skip3,'b');
    C=C.';
    C1=[C1,C];
    fseek(fid,18,'bof');
    D=fread(fid,inf,precision4,skip4);
    D01=reshape(D,[4096,length(D)/4096]);
    D1=[D1,D01];
    fseek(fid,16408,'bof');
    E=fread(fid,inf,precision5,skip5);
    E1=reshape(E,[3,length(E)/3]);
    E2=[E2,E1];
    fclose(fid);
end