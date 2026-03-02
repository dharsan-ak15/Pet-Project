import requests

# 1. Login to get session and csrf token
client = requests.Session()
login_url = "http://127.0.0.1:8000/accounts/login/"
client.get(login_url) # Get initial CSRF cookie
csrf_token = client.cookies.get('csrftoken')

login_data = {
    'username': 'admin2',
    'password': 'admin2pass',
    'csrfmiddlewaretoken': csrf_token,
}
res = client.post(login_url, data=login_data, headers={'Referer': login_url})
print("Login Status Code:", res.status_code)

# 2. Upload image via profile endpoint
profile_url = "http://127.0.0.1:8000/accounts/profile/"
client.get(profile_url) # Refresh CSRF cookie for profile page
csrf_token = client.cookies.get('csrftoken')

image_path = "media/pets/shifu-dog.jpg"
try:
    with open(image_path, 'rb') as f:
        files = {'profile_image': ('test_image.jpg', f, 'image/jpeg')}
        data = {
            'first_name': 'Admin',
            'last_name': 'Two',
            'email': 'admin2@example.com',
            'phone': '9876543210',
            'csrfmiddlewaretoken': csrf_token,
        }
        res2 = client.post(profile_url, data=data, files=files, headers={'Referer': profile_url})
        print("Upload Status Code:", res2.status_code)
except Exception as e:
     print("Error opening test file:", e)
