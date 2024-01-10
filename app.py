from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random
from functools import lru_cache


def read_words_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file]


def generate_legible_color():
    # Generate a random color that is legible on white background
    # Avoid whites, yellows, and light colors
    min_brightness = 0.4  # Minimum brightness for legible colors
    while True:
        color = tuple(random.randint(0, 255) for _ in range(3))
        brightness = (0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]) / 255
        if brightness > min_brightness:
            return color


def generate_image_with_words(image_path, words):
    # Open the image file
    base_image = Image.open(image_path)
    base_array = np.array(base_image)

    # Get the image size
    image_width, image_height = base_image.size

    # Create a drawing object
    draw = ImageDraw.Draw(base_image)

    # Define the font and size
    font_size = 25
    font = ImageFont.truetype("calibri-regular.ttf", font_size)

    # Define the margin
    margin = 20

    # Tolerance for white color
    white_tolerance = 3

    # Function to check if two rectangles overlap
    def is_overlapping(rect1, rect2):
        return not (
            rect1[2] < rect2[0]
            or rect1[0] > rect2[2]
            or rect1[3] < rect2[1]
            or rect1[1] > rect2[3]
        )

    # Function to check if a position is in a white portion of the image
    @lru_cache(maxsize=None)
    def is_in_white_region(position):
        x, y = position[0], position[1]
        target_white = np.array([255, 255, 255])
        pixel = base_array[y, x][:3]  # Extract only RGB values, ignoring alpha (A)
        return np.all(np.abs(pixel - target_white) <= white_tolerance)

    # Function to generate random non-overlapping positions for words in white portions
    def get_random_position(word_size):
        while True:
            x = np.random.randint(margin, image_width - margin - word_size[0])
            y = np.random.randint(margin, image_height - margin - word_size[1])
            position = (x, y, x + word_size[0], y + word_size[1])
            if is_in_white_region(position) and not any(
                is_overlapping(position, existing_position)
                for existing_position in positions
            ):
                return position

    positions = []

    for word in words:
        # Get the size of the word
        word_size = draw.textlength(word, font), 1

        # Generate random position for the word in a white portion
        position = get_random_position(word_size)

        # Generate a random legible color for the word
        text_color = generate_legible_color()

        # Draw the word on the image with the generated color
        draw.text((position[0], position[1]), word, font=font, fill=text_color)

        # Save the position of the drawn word
        positions.append(position)

    # Save the final image
    base_image.save("output_image.png")


if __name__ == "__main__":
    image_path = "input.png"
    words = read_words_from_file("words.txt")

    generate_image_with_words(image_path, words)
