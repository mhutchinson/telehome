import configparser
import homeassistant.remote as remote
import os
import telepot
import time
from pprint import pprint
from telepot.namedtuple import ReplyKeyboardMarkup

telegram_bot_id = None
telegram_chat_whitelist = None

hass_ip = None
hass_pass = None

CMD_LIGHTS = '/lights'
DOMAIN_LIGHTS = 'light'

def handle(msg):
    chat_id = msg['chat']['id']

    if chat_id not in telegram_chat_whitelist:
        bot.sendMessage(chat_id, 'Sorry, my parents told me not to talk to strangers')

    command = msg['text']

    if command.startswith(CMD_LIGHTS):
        bot.sendMessage(chat_id, handle_lights(_strip_action(command, CMD_LIGHTS)))
    else:
        markup = ReplyKeyboardMarkup(keyboard=[
            ['/lights on', '/lights off', '/lights toggle', '/lights state']
        ])
        bot.sendMessage(chat_id, 'Available commands in buttons below', reply_markup=markup)
    pprint(msg)

def handle_lights(args):
    if args == 'toggle':
        remote.call_service(api, DOMAIN_LIGHTS, 'toggle')
        return 'Toggled lights'
    if args == 'on':
        remote.call_service(api, DOMAIN_LIGHTS, 'turn_on')
        return 'Turned lights on'
    if args == 'off':
        remote.call_service(api, DOMAIN_LIGHTS, 'turn_off')
        return 'Turned lights off'

    light = 'light.made_lamp'
    lamp = remote.get_state(api, light)
    if args == '' or args == 'state':
        return 'Made Lamp is ' + lamp.state
    else:
        return 'Unknown command ' + args + '. Supported commands: state, on, off, toggle'

def _strip_action(command, action):
    if not command.startswith(action):
        raise Exception(command + ' does not start with ' + action)
    return command[len(action):].strip()

def _read_config():
    config = configparser.ConfigParser()
    home_dir = os.path.expanduser('~')
    configfile = os.path.join(home_dir, '.telehome/config.txt')
    if not os.path.exists(configfile):
        raise Exception('Expected configuration file: ' + configfile)
    config.read(configfile)
    return config

config = _read_config()
hass_ip = config['homeAssistant']['ip']
telegram_bot_id = config['telegram']['botKey']
telegram_chat_whitelist = [int(config['telegram']['chatIdWhitelist'])]

print('Configured with hass_ip=%s bot_id=%s allowed_chat=%s' % (hass_ip, telegram_bot_id, telegram_chat_whitelist))
bot = telepot.Bot(telegram_bot_id)
api = remote.API(hass_ip, hass_pass)
status = remote.validate_api(api)
pprint(status)
if status != remote.APIStatus.OK:
    print('Failed to connect to home assistant')
    exit()

print ('starting loop')
bot.message_loop(handle)
while 1:
    time.sleep(10)
print ('finish loop')