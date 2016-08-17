set dt=rendergmaster-v{{ version }}
net use v: \\172.20.0.241\data\support\vhdx renderg /user:administrator
mkdir %dt%
del /f /s /q C:\\pagefile.sys
robocopy C:\\ v:\\%dt% /E /ETA
echo %date%-%time% > v:\\%dt%\\bak_time.txt
curl http://172.20.0.51:8080/service/notification_service_status/
wpeutil.exe reboot
