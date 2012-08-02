import sys
import urllib
import urllib2

schedule_form, login, password, schedule_file = sys.argv[1:]

schedule_data = open(schedule_file)
data_dict = {
    'form.data': schedule_data.read(),
    'form.actions.upload': 'Upload',
    }

post_data = urllib.urlencode(data_dict)

password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
top_level_url = schedule_form
password_mgr.add_password(None, top_level_url, login, password)
handler = urllib2.HTTPBasicAuthHandler(password_mgr)
opener = urllib2.build_opener(handler)

submit_result = opener.open(schedule_form, post_data)

print submit_result.read()
