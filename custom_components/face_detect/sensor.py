from homeassistant.components.sensor import PLATFORM_SCHEMA
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import logging
import requests
import time
from homeassistant.helpers.entity import Entity
import base64
import os
from datetime import timedelta
from aip import AipFace
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)
TIME_BETWEEN_UPDATES = timedelta(seconds=1)

CONF_OPTIONS = "options"
CONF_APP_ID = 'app_id'
CONF_API_KEY = 'api_key'
CONF_ENTITY_ID = 'entity_id'
CONF_SECRET_KEY = 'secret_key'
CONF_HOST = 'host'
CONF_PORT = 'port'
CONF_ACCESS_TOKEN = 'access_token'



OPTIONS = dict(age=["baidu_age", "年龄", "mdi:account", "岁"],
               beauty=["baidu_beauty", "颜值", "mdi:face-woman-shimmer", "分"],
               emotion=["baidu_emotion", "情绪", "mdi:emoticon-excited-outline", None],
               gender=["baidu_gender", "性别", "mdi:gender-female", None],
               glasses=["baidu_glasses", "眼镜识别", "mdi:glasses", None],
               expression=["baidu_expression", "表情", "mdi:emoticon-neutral-outline", None]
               )

ATTR_UPDATE_TIME = "更新时间"
ATTRIBUTION = "Powered by BaiDuAI"
ATTRIBUTION_POWER = "强力支持"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {   vol.Required(CONF_OPTIONS, default=[]): vol.All(cv.ensure_list, [vol.In(OPTIONS)]),
        vol.Required(CONF_APP_ID): cv.string,
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_SECRET_KEY): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.string,
        vol.Required(CONF_ENTITY_ID): cv.string,
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.info("Setup platform sensor.face_detect")
    save_path = hass.config.path('custom_components/face_detect/www/')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    appid = config.get(CONF_APP_ID)
    apikey = config.get(CONF_API_KEY)
    secretkey = config.get(CONF_SECRET_KEY)
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    cameraid = config.get(CONF_ENTITY_ID)
    accesstoken = config.get(CONF_ACCESS_TOKEN)

    data = FaceDetectdata(appid, apikey, secretkey, host, port, cameraid, accesstoken, save_path)

    dev = []
    for option in config[CONF_OPTIONS]:
        dev.append(FaceDetectSensor(data,option))
    add_entities(dev, True)
     


class FaceDetectSensor(Entity):
    def __init__(self, data, option):
        self._data = data
        self._object_id = OPTIONS[option][0]
        self._friendly_name = OPTIONS[option][1]
        self._icon = OPTIONS[option][2]
        self._unit_of_measurement = OPTIONS[option][3]
        self._type = option
        self._state = None
        self._updatetime = None

    @property
    def unique_id(self):
        return self._object_id

    @property
    def name(self):
        return self._friendly_name

    @property
    def icon(self):
        return self._icon
    @property

    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property  
    def extra_state_attributes(self):
        global ATTRIBUTION

        ATTRIBUTION = "Powered by BaiDuAI"

        return {
            ATTR_UPDATE_TIME: self._updatetime,
            ATTRIBUTION_POWER: ATTRIBUTION,
        }


    def update(self):
        self._data.update()
        self._updatetime = self._data.updatetime

        if self._type == "age":
            self._state = self._data.age
        elif self._type == "beauty":
            self._state = self._data.beauty
        elif self._type == "emotion":
            self._state = self._data._emotion
        elif self._type == "gender":
            self._state = self._data.gender
        elif self._type == "glasses":
            self._state = self._data.glasses
        elif self._type == "expression":
            self._state = self._data.expression


class FaceDetectdata(object):
    def __init__(self, appid, apikey, secretkey, host, port, cameraid, accesstoken, save_path):
        self._appid = appid
        self._apikey = apikey
        self._secretkey = secretkey
        self._host = host
        self._port = port
        self._save_path = save_path
        self._cameraid = cameraid
        self._accesstoken = accesstoken
        self._age = None
        self._beauty = None
        self._emotion = None
        self._gender = None
        self._glasses = None
        self._expression = None

    @property
    def age(self):
        return self._age

    @property
    def beauty(self):
        return self._beauty

    @property
    def emotion(self):
        return self._emotion

    @property
    def gender(self):
        return self._gender

    @property
    def glasses(self):
        return self._glasses
        
    @property
    def expression(self):
        return self._expression

    @property
    def updatetime(self):
        return self._updatetime
        
    def get_picture(self):
        t = int(round(time.time()))
        headers = {'Authorization': "Bearer {}".format(self._accesstoken),
               'content-type': 'application/json'}
        http_url = "http://{}:{}".format(self._host, self._port)
        camera_url = "{}/api/camera_proxy/{}?time={} -o image.jpg".format(http_url, self._cameraid, t)
        response = requests.get(camera_url, headers=headers)
        return response.content
        
    def save_picture(self, time, content, beauty):
        savepath = self._save_path + time + "---"+str(beauty) + '.jpg'
        if not os.path.exists(savepath):
            with open(savepath, 'wb') as fp:
                fp.write(content)
                fp.close()
                
    def baidu_facedetect(self):
        self._client = AipFace(self._appid, self._apikey, self._secretkey)
        img_data = self.get_picture()
        data = base64.b64encode(img_data)
        image = data.decode()
        imageType = "BASE64"
        self._client.detect(image, imageType)
        options = {}
        options["face_field"] = "beauty,age,faceshape,expression,emotion,gender,glasses"
        options["max_face_num"] = 1
        options["face_type"] = "LIVE"
        res = self._client.detect(image, imageType, options)
        return res,img_data
    
    @Throttle(TIME_BETWEEN_UPDATES)
    def update(self):
        try :
            res,img_data = self.baidu_facedetect()
        except Exception as e:
            logging.info(e)
        _LOGGER.info("Update from BaiDuAI...")

        try :

            self._age = res["result"]["face_list"][0]["age"]
            self._beauty = res["result"]["face_list"][0]["beauty"]
            
            emotion = res["result"]["face_list"][0]["emotion"]["type"]
            if (emotion == "angry"):
                emotion = "愤怒"
            elif (emotion == "disgust"):
                emotion = "厌恶"
            elif (emotion == "fear"):
                emotion = "恐惧"
            elif (emotion == "happy"):
                emotion = "高兴"
            elif (emotion == "sad"):
                emotion = "伤心"
            elif (emotion == "surprise"):
                emotion = "惊讶"
            elif (emotion == "neutral"):
                emotion = "无情绪"
            self._emotion = emotion
            
            gender = res["result"]["face_list"][0]["gender"]["type"]
            if (gender == "male"):
                gender = "男生"
            elif (gender == "female"):
                gender = "女生"
            self._gender = gender
            
            glasses = res["result"]["face_list"][0]["glasses"]["type"]
            if (glasses == "none"):
                glasses = "没有佩戴眼镜"
            elif (glasses == "common"):
                glasses = "普通眼镜"
            elif (glasses == "sun"):
                glasses = "墨镜"
            self._glasses = glasses
            
            expression = res["result"]["face_list"][0]["expression"]["type"]
            if (expression == "none"):
                expression = "没有微笑"
            elif (expression == "smile"):
                expression = "微笑"
            elif (expression == "laugh"):
                expression = "大笑"
            self._expression = expression
            self.save_picture(self._updatetime, img_data ,self._beauty)
        except Exception as e:
            logging.info(e)
        self._updatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            
            
            
          


