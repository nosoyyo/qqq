class QQQuotation():
    headers = {}
    headers['Host'] = 'qt.gtimg.cn'
    headers['Referer'] = 'http://gu.qq.com/usAAPL.OQ/gg'
    headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'

class Portfolio():

    symbols = [
        'IXIC',
        'INX',
        'AAPL',
        'FB',
        'TSLA',
        'TVIX',
        'NFLX',
        'ADBE',
        'MSFT',
    ]


class FeishuBot():

    app_id = 'cli_9e1f1b5c4439100e'
    app_secret = 'SS8ogLKeaX73q0YSorRhobxa3eK1qI4h'

    tiger_id = '20150741'
    account = '6200921'
    mock_account = '20200412183651716'
    private_pem_path = '/etc/ssl/certs/rsa_private_key.pem'

    total_funds = 4870
    my_server = 'http://129.211.173.161:8000/feishu'
    # ⬇this works but with unecessary com lag so better use ip directly
    # my_server = 'http://believemusic.cn:8000/feishu'

    # for testing
    UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.3.1 Mobile/15E148 Safari/604.1 Lark/3.21.9 LarkLocale/zh_CN SDK-Version/3.21.17'
    uuid = '0297921985f37c2860ae92a9a6c18bf2'
    open_id = 'ou_1f6925dcda1b3921a6066d3a1d0786fc'
    open_chat_id = 'oc_47ad1f01bf15c20e6b9e52e0e9d88e3e'
    open_message_id = 'om_df7135262b89168bc97d31b3e511b2ef'
    tenant_key = '2d0dd2c84c4f175e'
    at_open_id = "ou_ef8e6f5b6e58271b10ddddb8a6648be7"
    token = 'oAiuWxpz6Pgsf6Cl6hQwghq2pD7nL8h3'

    bot_groups = [{'avatar': 'https://lf3-ttcdn-tos.pstatp.com/img/lark.avatar/78c0000676df676a7f6e~100x100.jpg',
                   'chat_id': 'oc_a1a786d6f1066b5038a93d3124b44d50',
                   'description': '',
                   'name': 'MSFC⭐2020新的开始',
                   'owner_open_id': 'ou_b049a791f5571505579ff4e3703b81b8',
                   'owner_user_id': 'fc43c9e8'},
                  {'avatar': 'https://sf3-ttcdn-tos.pstatp.com/img/lark.avatar/78c1000669334ef745c0~100x100.jpg',
                   'chat_id': 'oc_47ad1f01bf15c20e6b9e52e0e9d88e3e',
                   'description': '',
                   'name': '狸助测试',
                   'owner_open_id': 'ou_1f6925dcda1b3921a6066d3a1d0786fc',
                   'owner_user_id': '8821bde1'}]
