from homeassistant.components.sensor import PLATFORM_SCHEMA
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import logging
import requests
import time
from homeassistant.helpers.entity import Entity
import base64
import os,datetime
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
CONF_GROUP_LIST = 'group_list'
CONF_DELETE_TIME = 'delete_time'

OPTIONS = dict(age=["baidu_age", "年龄", "mdi:account", "岁"],
               beauty=["baidu_beauty", "颜值", "mdi:face-woman-shimmer", "分"],
               emotion=["baidu_emotion", "情绪", "mdi:emoticon-excited-outline", None],
               gender=["baidu_gender", "性别", "mdi:gender-female", None],
               glasses=["baidu_glasses", "眼镜识别", "mdi:glasses", None],
               expression=["baidu_expression", "表情", "mdi:emoticon-neutral-outline", None],
               faceshape=["baidu_faceshape", "脸型", "mdi:baby-face-outline", None],
               facerecognition=["baidu_facerecognition", "人脸识别", "mdi:face-recognition", None]
               )

ATTRIBUTION_UPDATE_TIME = "更新时间"
ATTRIBUTION_CHECK = "识别状态"
ATTRIBUTION_POWER = "强力支持"
ATTRIBUTION_FACE = "人脸识别"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {   vol.Required(CONF_OPTIONS, default=[]): vol.All(cv.ensure_list, [vol.In(OPTIONS)]),
        vol.Required(CONF_APP_ID): cv.string,
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_SECRET_KEY): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.string,
        vol.Required(CONF_ENTITY_ID): cv.string,
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
        vol.Required(CONF_GROUP_LIST): cv.string,
        vol.Required(CONF_DELETE_TIME): cv.string
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.info("Setup platform sensor.face_detect")
    time.sleep(1)
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
    grouplist = config.get(CONF_GROUP_LIST)
    deletetime = config.get(CONF_DELETE_TIME)
    
    data = FaceDetectdata(appid, apikey, secretkey, host, port, cameraid, accesstoken, save_path, grouplist, deletetime)

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
        self._check = "否"
        self._face = "无"
        self._grouplist = None

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
        global ATTRIBUTION_POWER
        
        ATTRIBUTION__POWER = "Powered by BaiDuAI"
        

        return {
            ATTRIBUTION_UPDATE_TIME: self._updatetime,
            ATTRIBUTION_POWER: ATTRIBUTION__POWER,
            ATTRIBUTION_CHECK: self._check,
            ATTRIBUTION_FACE: self._face,
        }


    def update(self):
        self._data.update()
        self._updatetime = self._data.updatetime
        self._check = self._data.check
        self._face = self._data.face

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
        elif self._type == "facerecognition":
            self._state = self._data.facerecognition
        elif self._type == "faceshape":
            self._state = self._data.faceshape


class FaceDetectdata(object):
    def __init__(self, appid, apikey, secretkey, host, port, cameraid, accesstoken, save_path, grouplist, deletetime):
        self._appid = appid
        self._apikey = apikey
        self._secretkey = secretkey
        self._host = host
        self._port = port
        self._save_path = save_path
        self._cameraid = cameraid
        self._accesstoken = accesstoken
        self._grouplist = grouplist
        self._deletetime = deletetime
        self._age = None
        self._beauty = None
        self._emotion = None
        self._gender = None
        self._glasses = None
        self._expression = None
        self._faceshape = None
        self._facerecognition = None

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
    def faceshape(self):
        return self._faceshape

    @property
    def updatetime(self):
        return self._updatetime
        
    @property  #识别状态
    def check(self):
        return self._check
    
    @property  #人脸识别（属性)
    def face(self):
        return self._face

    @property  #人脸识别（实体)
    def facerecognition(self):
        return self._facerecognition
        
        
    def get_picture(self):
        t = int(round(time.time()))
        headers = {'Authorization': "Bearer {}".format(self._accesstoken),
               'content-type': 'application/json'}
        try:
            http_url = "http://{}:{}".format(self._host, self._port)
            camera_url = "{}/api/camera_proxy/{}?time={} -o image.jpg".format(http_url, self._cameraid, t)
            response = requests.get(camera_url, headers=headers)
        except:
            http_url = "https://{}:{}".format(self._host, self._port)
            camera_url = "{}/api/camera_proxy/{}?time={} -o image.jpg".format(http_url, self._cameraid, t)
            response = requests.get(camera_url, headers=headers)
        return response.content
        
    def save_picture(self, content, age, emotion, beauty, gender):
        savepath = self._save_path + str(age) + "-" + str(emotion) + "-" + str(beauty) + "-" + str(gender) + '.jpg'
        if not os.path.exists(savepath):
            with open(savepath, 'wb') as fp:
                fp.write(content)
                fp.close()
                
    def removefile(self):
        path = self._save_path #需要清空的文件夹
        files = list(os.walk(path)) #获得所有文件夹的信息列表
        delta = datetime.timedelta(seconds=int(self._deletetime)) #设定过期时间
        now = datetime.datetime.now() #获取当前时间
        for file in files: #遍历该列表
            os.chdir(file[0]) #进入本级路径，防止找不到文件而报错
            if file[2] != []: #如果该路径下有文件
                for x in file[2]: #遍历这些文件
                    ctime = datetime.datetime.fromtimestamp(os.path.getctime(x)) #获取文件创建时间
                    print(ctime)
                    if ctime < (now-delta): 
                        os.remove(x)    
                            
                        
    def baidu_facedetect(self):
        self._client = AipFace(self._appid, self._apikey, self._secretkey)
        img_data = self.get_picture()
        data = base64.b64encode(img_data)
        image = data.decode()
        imageType = "BASE64"
        self._client.detect(image, imageType)
        #人脸检测
        options = {}
        options["face_field"] = "beauty,age,faceshape,expression,emotion,gender,glasses"
        options["max_face_num"] = 1
        options["face_type"] = "LIVE"
        res1 = self._client.detect(image, imageType, options)
        #人脸搜索
        options = {}
        options["max_face_num"] = 1
        options["match_threshold"] = 70
        options["quality_control"] = "NORMAL"
        options["liveness_control"] = "LOW"
        options["max_user_num"] = 1
        res2 = self._client.multiSearch(image, imageType, self._grouplist, options)

        return res1,img_data,res2
    
    @Throttle(TIME_BETWEEN_UPDATES)
    def update(self):
        try:
            res1, img_data, res2 = self.baidu_facedetect()
        except:
            res1 = {"result":None}
            
        _LOGGER.info("Update from BaiDuAI...")
        if (res1["result"] is  None):
            self._check = "否"
        else :
            self._check = "是"
        try :

            self._age = res1["result"]["face_list"][0]["age"]
            self._beauty = res1["result"]["face_list"][0]["beauty"]
            
            emotion = res1["result"]["face_list"][0]["emotion"]["type"]
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
            elif (emotion == "grimace"):
                emotion = "鬼脸"
            elif (emotion == "pouty"):
                emotion = "翘嘴"
            self._emotion = emotion
            
            gender = res1["result"]["face_list"][0]["gender"]["type"]
            if (gender == "male"):
                gender = "男生"
            elif (gender == "female"):
                gender = "女生"
            self._gender = gender
            
            glasses = res1["result"]["face_list"][0]["glasses"]["type"]
            if (glasses == "none"):
                glasses = "没有佩戴眼镜"
            elif (glasses == "common"):
                glasses = "普通眼镜"
            elif (glasses == "sun"):
                glasses = "墨镜"
            self._glasses = glasses
            
            expression = res1["result"]["face_list"][0]["expression"]["type"]
            if (expression == "none"):
                expression = "没有微笑"
            elif (expression == "smile"):
                expression = "微笑"
            elif (expression == "laugh"):
                expression = "大笑"
            self._expression = expression
            
            faceshape = res1["result"]["face_list"][0]["face_shape"]["type"]
            if (faceshape == "square"):
                faceshape = "正方形脸"
            elif (faceshape == "triangle"):
                faceshape = "三角形脸"
            elif (faceshape == "oval"):
                faceshape = "椭圆脸"
            elif (faceshape == "heart"):
                faceshape = "心型脸"
            elif (faceshape == "round"):
                faceshape = "圆型脸"
            self._faceshape = faceshape
            
            self.save_picture(img_data , self._age, self._emotion, self._beauty, self._gender)
            
            self._face = res2["result"]["face_list"][0]["user_list"][0]["user_id"]
            self._facerecognition = res2["result"]["face_list"][0]["user_list"][0]["user_id"]
        except Exception as e:
            self._face = "无"
            self._facerecognition = "无"
            logging.info(e)
        self._updatetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.removefile()
