import os.path
from typing import List, Any


class Image:
    # Constants
    _FILE_SIGNATURE = b'LIMG'
    Format_BW = 0

    def __init__(self, array: List[List[Any]], image_format: int):
        """
        Create the object from an array

        :param array: The array to use as a source
        :param image_format: The format of the array
        :raises ValueError: if path points to invalid file
        """

        def validate_array(array: List[List[Any]]):
            if self._image_format == self.Format_BW:
                # B & W mode, pixels should be either 1 or 0
                for row in array:
                    for pixel in row:
                        if int(pixel) not in [0, 1]:
                            raise ValueError("Format_BW pixels should have a value of 0 or 1.")

        self._data = array
        self._image_format = image_format

        self._height = len(array)
        self._width = len(array[0])

        # Check that array has same row length on every row
        for row in self._data:
            if len(row) != self._width:
                raise ValueError("Every line in the array must have the same length.")

        try:
            validate_array(self._data)
        except ValueError as e:
            print("Invalid image file: {}".format(str(e)))
            raise ValueError("Invalid image file, check logs for details.")

    @classmethod
    def from_file(cls, filepath: str):
        """
        Creates an object based on a file

        :param filepath: file of the path to use
        :return: An Image object
        :raises ValueError: if the filepath points to an invalid file
        """

        def binary_to_data(binary: bytes, image_format: int, width: int, height: int) -> List[List[Any]]:
            # Convert bytes to binary string
            binary_str = ""
            for byte in binary:
                binary_str += "{0:08b}".format(byte)

            result = [[0 for _ in range(width)] for _ in range(height)]  # Creates array with specified dimensions
            if image_format == cls.Format_BW:
                # B & W, each pixel is a single bit of 1 or 0
                i = 0
                for row in range(len(result)):
                    for col in range(len(result[0])):
                        result[row][col] = int(binary_str[i])
                        i += 1
            return result

        # Check that file exists
        if not os.path.isfile(filepath):
            raise ValueError(filepath + " doesn't exist.")

        file = open(filepath, 'rb')

        # Check signature
        signature = file.read(4)
        if signature != cls._FILE_SIGNATURE:
            raise ValueError(filepath + " doesn't seem to point to a limg file.")

        # Read dimensions
        width = int.from_bytes(file.read(2), "big")
        height = int.from_bytes(file.read(2), "big")

        # Read image format
        image_format = int.from_bytes(file.read(1), "big")

        # Read data
        data = file.read()
        file.close()

        # Convert data from binary to pixel array
        data = binary_to_data(data, image_format, width, height)
        return Image(data, image_format)

    def write_to_file(self, path: str) -> None:
        """
        Writes the Image to a file

        :param path: The path of the file to write to
        """

        def data_to_binary() -> str:
            """
            Takes the _data array and creates its binary representation based on the _image_format

            :return: The binary representation to write to a file.
            """

            result = ""
            if self._image_format == self.Format_BW:
                # Data is already in bits, append each pixel to result
                for row in self._data:
                    for pixel in row:
                        result += str(pixel)
            return result

        # Create the path
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Append file signature if not present
        if path[-5:] != ".limg":
            path += ".limg"

        file = open(path, 'wb')
        file.write(self._FILE_SIGNATURE)

        binary_data = ""

        # Write image dimension (2 bytes per dimension)
        binary_data += "{0:016b}{1:016b}".format(self._width, self._height)

        # Write image mode byte
        binary_data += "{0:08b}".format(self._image_format)

        # Write data to file
        binary_data += data_to_binary()

        # pad end with 0s to fill bytes
        missing = 8 - len(binary_data) % 8
        missing = 0 if missing == 8 else missing  # if "missing" 8, already full
        binary_data += "0" * missing

        # Split in bytes and convert to base 10
        bytes_array = [int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8)]
        file.write(bytes(bytes_array))
        file.close()

    def get_width(self) -> int:
        return self._width

    def get_height(self) -> int:
        return self._height

    def get_image_format(self) -> int:
        return self._image_format

    def to_array(self) -> List[List[str]]:
        # convert every element into a string to have a uniform export
        return [[str(i) for i in row] for row in self._data]
