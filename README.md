# MIAcloud


## How to test

### Cloud
curl -u user:pass -i -X POST -F "file=@/Users/=/Desktop/PythonGitHub/openshift/miacloud/IM-0001-0054.dcm" http://miacloud-panagiotis.rhcloud.com/upload?email=a@a.com

### Local 

curl -u user:user -i -X POST -F "file=@/Users/m112447/Desktop/PythonGitHub/openshift/miacloud/IM-0001-0054.dcm" http://127.0.0.1:5000/?email=a@a.com

## How to set env variables in openshift gears

This is very useful for setting up the email password. 

rhc set-env MAIL_USERNAME=VALUE1 MAIL_PASSWORD=VALUE2  APPUSER=VALUE3 APPPASS=VALUE4 -a appname 