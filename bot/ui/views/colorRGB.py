import aiohttp
from PIL import Image
from collections import Counter
from io import BytesIO

class DominantColor:
    async def fetch_image(url, width=100, height=100):
        # Используем параметры запроса для изменения размера изображения
        modified_url = f"{url}?width={width}&height={height}"
        async with aiohttp.ClientSession() as session:
            async with session.get(modified_url) as response:
                return await response.read()

    async def get_dominant_color(image_url, width=100, height=100):
        try:
            image_data = await DominantColor.fetch_image(image_url, width, height)
            image = Image.open(BytesIO(image_data))
            pixels = list(image.getdata())
            sum_red, sum_green, sum_blue = 0, 0, 0

            for pixel in pixels:
                sum_red += pixel[0]
                sum_green += pixel[1]
                sum_blue += pixel[2]

            avg_red = sum_red // len(pixels)
            avg_green = sum_green // len(pixels)
            avg_blue = sum_blue // len(pixels)

            return avg_red, avg_green, avg_blue
        except:
            return (0, 0, 0)
