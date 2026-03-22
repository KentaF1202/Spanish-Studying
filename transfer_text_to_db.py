import requests

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2IiwiZXhwIjoxNzc0MjIxNzMxfQ.zHNgyXBFUtaH62qaaSLY1KNpAdRC-Vi8g5GE4FOdpt0"
URL = "https://spanishmaxxing.app/api/vwords/"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

successful = {}
fail = {}

for chapter in range(1,5):
    filename = "textbook_vocab/chapter_" + str(chapter) + ".txt"
    print(filename)
    print("---------------------------------------------------------------------")
    with open(filename, mode="r", encoding="utf-8") as file:
        content = file.read()
        entries = content.split("\n")

        for entry in entries:
            spanish, english = entry.split("\\")
            print(f"{english=}")
            print(f"{spanish=}")

            list_id = chapter+4
            payload = {
                "list_id": list_id,
                "english": english,
                "spanish": spanish
            }
            response = requests.post(URL, headers=headers, json=payload)

            if response.status_code == 201 or response.status_code == 200:
                successful[english] = spanish
            else:
                fail[english] = spanish

print(f"{fail=}")