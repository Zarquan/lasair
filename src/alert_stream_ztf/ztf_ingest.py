#!/home/roy/anaconda2/bin/python
# This runs in a crontab. Works out todays date to make the topic
# Sucks in the alerts and puts them in the database
# Converts the FITS to jpegs in the "post ingest" phase
# crontab entry is
# 0/15 * * * * /home/roy/lasair/src/alert_stream_ztf/ztf_ingest.py

import os,sys
sys.path.append('/home/roy/lasair/src/alert_stream_ztf/common')

import date_nid

if len(sys.argv) > 1:
    nid = int(sys.argv[1])
else:
    nid  = date_nid.nid_now()

date = date_nid.nid_to_date(nid)
topic  = 'ztf_' + date + '_programid1'
print("Topic is %s, nid is %d" % (topic, nid))

cmd =  '/home/roy/anaconda3/bin/python bin/ingestStreamThreaded.py '
cmd += '--logging INFO '
cmd += '--stampdump %d ' % nid
cmd += '--maxalert 20000 '
cmd += '--nthread 4 '
cmd += '--group LASAIR '
cmd += '--host public.alerts.ztf.uw.edu '
cmd += '--topic ' + topic

os.system('date')
print(cmd)
os.system(cmd)

tail = 'tail -2 /data/ztf/logs/' + topic + '.log'
os.system(tail)

cmd = '/home/roy/anaconda3/bin/python /home/roy/lasair/src/post_ingest/coverage.py %d' % nid
os.system(cmd)

cmd = '/home/roy/anaconda3/bin/python /home/roy/lasair/src/post_ingest/check_status.py %d' % nid
os.system(cmd)

cmd = '/home/roy/anaconda3/bin/python /home/roy/lasair/src/post_ingest/jpg_stamps.py /data/ztf/stamps/fits/%d /data/ztf/stamps/jpg/%d' % (nid, nid)
os.system(cmd)

cmd = '/home/roy/anaconda3/bin/python /home/roy/lasair/src/post_ingest/update_objects.py'
os.system(cmd)

cmd = '/home/roy/anaconda3/bin/python /home/roy/lasair/src/post_ingest/get_number_candidates.py'
os.system(cmd)

os.system('date')
