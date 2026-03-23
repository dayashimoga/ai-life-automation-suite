import urllib.request

try:
    # A busy street with people and cars
    urllib.request.urlretrieve(
        "https://images.unsplash.com/photo-1517646287270-a5a9ca602e5c?w=800&q=80",
        "busy_street.jpg",
    )
    print("Downloaded busy_street.jpg")
except Exception as e:
    print(f"Failed to download image: {e}")
