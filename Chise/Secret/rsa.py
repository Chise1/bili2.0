# -*- encoding: utf-8 -*-
"""
@File    : __init__.py.py
@Time    : 2020/6/3 11:02
@Author  : chise
@Email   : chise123@live.com
@Software: PyCharm
@info    :加密包使用
"""
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

PublicKey = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCsEef8bPDSqkDfq6gvjUFIQZ2I
GEoJchmQR5sqUZvZZvsDt0mshqvuF+0sCCkQfL9Usd29y7Bhi4zNYQF96wxDRh/F
lat4Ewepl9mZznIR7oxlauJSQR0CMwB/rR/fOsDWwf21/nLe7Mgyy6IRZInTUSb9
cmptziIcM9c2EvWemwIDAQAB
-----END PUBLIC KEY-----
"""
PrivateKey = """-----BEGIN PRIVATE KEY-----
MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAKwR5/xs8NKqQN+r
qC+NQUhBnYgYSglyGZBHmypRm9lm+wO3SayGq+4X7SwIKRB8v1Sx3b3LsGGLjM1h
AX3rDENGH8WVq3gTB6mX2ZnOchHujGVq4lJBHQIzAH+tH986wNbB/bX+ct7syDLL
ohFkidNRJv1yam3OIhwz1zYS9Z6bAgMBAAECgYBYj+LJ/jw5AV3ggVZQGzDlgrgU
6wN4NxzHMMPBFT3UuHcro3Os86ecJP5yMkUIclx7uAw7+pFus0emEW6WI5ssUFZd
bpQJMA26kk7c2g3LUtcD4cefHVZYnRTrZCkxfltDEg4wt6FvRT2fl1GYTqTM21H+
I251RSLXnOrLVitmQQJBAOGq1TjW2/H6Fjb9GInf4BKYxGsdI1MyIYInaxrpbmJf
qTSqL6V+vg6Baxz/8ElP7wYSiUqASNcnkUNF7JjKReECQQDDMsxtTb1JahYhF2fQ
PhfWdE9t3d9kZJzr2hnxoWbSroi21rAB4t7nNcfpCGR71tCwVP2ySechAhx/79eX
EHv7AkBpIC4INn9rsDcdEraVtAcsYqJNy9si7J2Thk1s0gWsKigm8okTrYFYPI3r
iocjf+s3hvcSD8TfBf2zuyVG4CPBAkBZNRsGDRQnvAr2/ppcKjR8ttUiEdcpK24n
v5pBupCiUk96t+ziP8u9APAmyMYbbpYbMAxtcabmh+98bKErkcYHAkBNa/4iO6k6
/F/W/kCf8N1yxzvUTcK7GbUSA0f5uJzVf1qbzBM6sA5zjw/XKvIvVZHa3juMJQQ6
PwVB3u+IcERp
-----END PRIVATE KEY-----
"""


def rsa_long_encrypt(msg: str, length=100) -> bytes:
    """
    长文本rsa加密
    单次加密串的长度最大为 (key_size/8)-11
    1024bit的证书用100， 2048bit的证书用 200
    """

    msg = base64.b64encode(msg.encode("utf-8"))
    pubobj = RSA.importKey(PublicKey)
    pubobj = PKCS1_v1_5.new(pubobj)
    res = []
    for i in range(0, len(msg), length):
        res.append(pubobj.encrypt(msg[i:i + length]))
    return b"".join(res)


def rsa_long_decrypt(message: bytes, default_length=128) -> str:
    """长文本解密"""
    # msg = base64.b64decode(message)
    msg = message
    length = len(msg)
    # default_length = 256
    # 私钥解密
    priobj = PKCS1_v1_5.new(RSA.importKey(PrivateKey))
    # 长度不用分段
    if length < default_length:
        return b''.join(priobj.decrypt(msg, b'ubout'))
    # 需要分段
    offset = 0
    res = []
    while length - offset > 0:
        if length - offset > default_length:
            res.append(priobj.decrypt(msg[offset:offset + default_length], b'ubout'))
        else:
            res.append(priobj.decrypt(msg[offset:], b'ubout'))
        offset += default_length
        m = b''.join(res)
        n = m.decode("utf-8")
        # print(n)
    return base64.b64decode(n).decode('utf-8')


if __name__ == "__main__":
    x = "我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊我是张三啊"
    encrypt_x = rsa_long_encrypt(x)
    print(str(encrypt_x))
    exec('x=' + str(encrypt_x))
    print(x)
    print(rsa_long_decrypt(encrypt_x))
