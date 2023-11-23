# Inference Dispatch Service on Amazon EC2 Server

## how to launcher service
1. buy EC2 instance server on Amazon, choose ubuntu22.04 OS
2. git clone this repository
3. ```sh prepare.sh```
4. fill AK, SK in run_server.sh
5. update model and endpoints in endpoints.ini
6. ```nohup sh run_server.sh &```

You can also add this job into crontab when server reboot
```bash
crontab -e
###
@reboot sh /path/to/aws_inference/run_server.sh &
```
