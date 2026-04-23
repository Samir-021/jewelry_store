import hmac
import hashlib
import base64
import json

user_data = '{"transaction_code":"000EAIN","status":"COMPLETE","total_amount":"10000.0","transaction_uuid":"587bb587-2c9d-4d20-81f3-08ae6540172","product_code":"EPAYTEST","signed_field_names":"transaction_code,status,total_amount,transaction_uuid,product_code,signed_field_names","signature":"D9gQe9y4VIW+CIwxRH1qTiXFH6rlcpLx0nvzEQZ6gww="}'
data = json.loads(user_data)
received_sig = data.get('signature')

fields = data['signed_field_names'].split(',')
keys = ["8gBm/:&EnhH.1/q", "8gBm/:&EnhH.1/q("]

delimiters = [",", "&", "|", ":", " "]
formats = [
    lambda d, f, sep: sep.join([f"{field}={d[field]}" for field in f]),
    lambda d, f, sep: sep.join([str(d[field]) for field in f]),
]

for key in keys:
    for sep in delimiters:
        for fmt in formats:
            msg = fmt(data, fields, sep)
            sig = base64.b64encode(hmac.new(key.encode(), msg.encode(), hashlib.sha256).digest()).decode()
            if sig == received_sig:
                print(f"MATCH! Key: {key}, Format: {msg}")
                exit()

print("No match found in brute force.")
