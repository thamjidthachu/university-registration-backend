import schedule
import time
import urllib.request as urllib, urllib as lib, json


class saved_last:
    last_id = 1548124


def SmsWaitingPay():

    try:
        while True:
            request = urllib.Request("https://my.um.edu.sa/backend/sms/waiting/pay/run", json.dumps({"last_id":saved_last.last_id}).encode("utf-8"))
            request.add_header('Content-Type', 'application/json; charset=utf-8')
            request.get_method = lambda: 'POST'
            response = urllib.urlopen(request)
            response = json.loads(response.read().decode("utf-8"))
            if isinstance(response, dict):
                if 'last_id' in response and 'total' in response:
                    if response['total'] > response['last_id']:
                        saved_last.last_id = response['last_id']
                    else:
                        break
                else:
                    break
            else:
                break

    except lib.error.URLError as e:
        fn = open("log_sms_waiting_pay", "a+")
        fn.write(str(e.read()) + "\n<------------------------------------------------------------------------>\n")
        fn.close()


schedule.every(12).hours.do(SmsWaitingPay)

while True:
    schedule.run_pending()
    time.sleep(1)
