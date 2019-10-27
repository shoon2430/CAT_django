import base64
import hashlib

from Cryptodome import Random
from Cryptodome.Cipher import AES
import time
from cat.settings import MY_SECRET_KEY

#암호화 모듈
BS = 16
pad = lambda s: s + (BS - len(s.encode('utf-8')) % BS) * chr(BS - len(s.encode('utf-8')) % BS)
unpad = lambda s : s[:-ord(s[len(s)-1:])]

class AESCIPER:
    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw.encode('utf-8') ) )

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] ))


data = '1234'


MY_SECRET_KEY = "HELLO~"

mykey =hashlib.sha256(MY_SECRET_KEY.encode('utf-8')).digest()


encrypted_data = AESCIPER(bytes(mykey)).encrypt(data)
encrypted_data
print(encrypted_data)

R1 = b'tC+nATWsEKpUMEFiXlhhxJFGe15DbHKi9ojYr6sjaQc='
print("R1 : ",R1)
R2 = str(R1)[2:-1]
print("R2 : ",R2)
R3 = R2.encode('utf-8')
print("R3 : ",R3)

decrypted_data = AESCIPER(bytes(mykey)).decrypt(R3)
print(decrypted_data.decode('utf-8'))

# R = b'xKByp4QA3EDJhgkFDHesC1s14JkaqdDr/iMAYi3v3dY='
#
# test = "bNQq5S/3cmFgD7IAG4j9gPVwIkE59xsD8DzZa+YmxFY="
# imsi = b'MaKhNN6ELmowWNKjw8ULnjVFLmD60yzngbJbv0qP5FI='
#
# P = str(R)[2:-1]
# T = test.encode('utf-8')
# print("{P : ",P)
# print(T)
# P = P.encode('utf-8')

# decrypted_data = AESCIPER(bytes(key)).decrypt(encrypted_data)
# decrypted_data.decode('utf-8')
# print(decrypted_data.decode('utf-8'))
# print(decrypted_data.decode('utf-8'))

# decrypted_data = AESCIPER(bytes(key)).decrypt(P)
# print(decrypted_data.decode('utf-8'))
#
# decrypted_data = AESCIPER(bytes(key)).decrypt(imsi)
# print(decrypted_data.decode('utf-8'))