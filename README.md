# 百度人脸识别插件v1.0

# 更新时间：2022/1/18


# 提前告知  本应用需要有摄像头

## 使用方法：

- 第一步，在HomeAssistant根目录中中建立以下文件夹
```
bash
mkdir custom_components
```
- 第二步，将face_detect文件夹放入custom_components文件夹中 
- 第三步，重启HomeAssistant
- 第四步，前往[百度AI开放平台创建人脸识别应用](https://console.bce.baidu.com/ai/?fromai=1#/ai/face/overview/index)，本应用需要用到appid，apikey，secretkey
![百度AI](baidu.png)
- 第五步，在HA中创建一个令牌


## configuration.yaml内容如下

``` yaml
sensor:
  - platform: face_detect
    app_id: "*****"  #百度人脸识别应用的appid
    api_key: "*****" #百度人脸识别应用的apikey
    secret_key: "*****" #百度人脸识别应用的secret_key
    entity_id: "*****" #摄像头的实体id
    access_token: "*****" #Homeassistant的令牌
    host: "*****" #运行Homeassistant的ip地址
    port: "*****" #运行Homeassistant的端口
    options: #可选识别的类型
      - age #年龄
      - beauty #颜值打分
      - emotion #情绪
      - gender #性别
      - glasses #佩戴眼镜识别
      - expression #表情
```
