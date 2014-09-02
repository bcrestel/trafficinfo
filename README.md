trafficinfo
===========

Description:
Text live traffic info to the mobile phone of your choice. Give it two road maps
with alternate road information and it will compare both roads for 30 min from
the time you set it and text it to you if there is any change.


How to run the script:
To let the script run permanently on your machine, type: 
nohup python trafficinfo.py &


What you need to do before you run it:
- Module requirements listed in requirements.txt
- Script uses gmail account. You need to enter your credentials in a dict named
  'myconfig.gmail.py'. It will looks like that:

email = dict(
    username = 'my_user_name',
    password = 'my_secret_password'
)

- The script relies on the Nokia traffic info for which you also need
  credentials. They must be entered as a dict in a file names
'HERE_credentials.py' with keys 'App_id' and 'App_Code'.

- You need to specify your phone number along with provider. So far the script
  accepts Virgin and AT&T. Place the information on a single line (phone number,
followed by provide) inside the file 'phonenumbers.txt'. You can specify several
phone numbers, but put each one on a different line. For example,

xxxxxxxxxx Virgin
xxxxxxxxxx ATT

- The script assumes your doing the trip 4 times a day, twice in each direction.
  'NB' stands for north bound. You will most likely want to modify the time for
each trips. You must also specify NB and SB roadmaps with ideal route (e.g,
highway) and alternate route (e.g, smaller road). The trip must be split in
several parts. Each part is number 'Part1', 'Part2',.... And each checkpoint is
given in GPS coordinates. Inside each part, you must specify the direct distance
between the 2 coordinates you gave (this is for checking; distances are in
meters). Conclude with keyword 'End'. For example,

Part1
xx.xxxxx, -xx.xxxx
xx.xxxxx, -xx.xxxx, 1000
Part2
xx.xxxxx, -xx.xxxx
xx.xxxxx, -xx.xxxx, 1800
xx.xxxxx, -xx.xxxx, 250
Part3
xx.xxxxx, -xx.xxxx
xx.xxxxx, -xx.xxxx, 3500
End

