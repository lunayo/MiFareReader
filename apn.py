from apns import APNs, Payload

apns = APNs(use_sandbox=True, cert_file='cert.pem', key_file='key.pem')

# Send a notification
token_hex = 'a5f8877b7c3126bfdbc58604a3a25f74bc573b44960fdb917559b1e3ce6f6cd1'
payload = Payload(alert="Employee working hours exceed 50", sound="default", badge=1)
apns.gateway_server.send_notification(token_hex, payload)
