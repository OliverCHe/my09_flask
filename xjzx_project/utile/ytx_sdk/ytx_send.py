from .CCPRestSDK import REST
# import ConfigParser

# 主帐号
accountSid = '8aaf0708635e4ce001638787b49e18af'

# 主帐号Token
accountToken = '5f90b6f6ec3e439d95d273dc42876e2f'

# 应用Id
appId = '8aaf0708635e4ce001638787b4f618b6'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'

# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id

def sendTemplateSMS(to, datas, tempId):

    # 初始化REST SDK
    rest = REST(serverIP, serverPort, softVersion)
    rest.setAccount(accountSid, accountToken)
    rest.setAppId(appId)

    result = rest.sendTemplateSMS(to, datas, tempId)
    return result.get('statusCode')
