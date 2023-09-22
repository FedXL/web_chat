import os

async def download_file_from_client_to_server(command: str, file, user_id):
    command = command.replace('/', '').split(" ")[1]
    downloaded_file = file
    directory_prefix = 'static/images'
    directory_path = os.path.join(directory_prefix, str(user_id))
    os.makedirs(directory_path, exist_ok=True)
    image_path = f'static/images/{user_id}/{command}.jpg'
    with open(image_path, 'wb') as f:
        f.write(downloaded_file.read())
    return image_path
