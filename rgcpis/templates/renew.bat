set dt=rendergmaster-v{{ version }}
net use v: \\172.20.0.241\data\support\vhdx renderg /user:administrator
diskpart -s diskpart.script
robocopy v:\\%dt% C:\\ /E /ETA
echo %date%-%time% > c:\\install_time.txt
curl http://172.20.0.51:8080/service/notification_service_status/
wpeutil.exe reboot

