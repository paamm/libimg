import os.path
from typing import List, Any, Union

_FILE_SIGNATURE = b'LIMG'


class Image:
    def __init__(self, data: Union[List[List[Any]], str]):
        """
        Create a new Image from a file or a 2D array

        :param data: The path of the file or the 2D array to use
        :raises ValueError: if matrix is invalid
        :raises ValueError: if path points to invalid file
        :raises ValueError: if data has an invalid format
        """
        if type(data) == list:
            # Load from array
            self._from_array(data)
        elif type(data) == str:
            self._from_file(data)
        else:
            # Invalid type for data
            raise ValueError("Data must be either a 2D list or a path to a file.")

    def _from_array(self, array: List[List[Any]]):
        """
        Create the object with an array as the source

        :param array: The array to use
        """
        self._data = array

        self._height = len(array)
        # Make sure array is same length horizontally everywhere
        self._width = len(array[0])
        for line in self._data:
            if len(line) != self._width:
                raise ValueError("Every line in the array must have the same length.")

        self._data = array

    def _from_file(self, path: str) -> None:
        """
        Create the object by reading a file from disk

        :param path: The path of the file to read
        """

        # Check if file exists
        if not os.path.isfile(path):
            raise ValueError(path + " doesn't exist.")

        file = open(path, 'rb')

        # Make sure correct file type (file signature)
        signature = file.read(4)
        if signature != _FILE_SIGNATURE:
            raise ValueError(path + " doesn't seem to point to a limg file.")

        # Read width/height bytes
        self._width = int.from_bytes(file.read(2), "big")
        self._height = int.from_bytes(file.read(2), "big")
        data = file.read()
        file.close()

        # Read the image bytes and create a "stream" by converting to bytes to binary
        data_stream = ""
        for byte in data:
            data_stream += "{0:08b}".format(byte)

        # Fill _data
        i = 0
        self._data = [[0 for _ in range(self._width)] for _ in range(self._height)]
        for row in range(self._height):
            for col in range(self._width):
                self._data[row][col] = int(data_stream[i])
                i += 1

    def write_to_file(self, path: str) -> None:
        """
        Writes the Image to a file

        :param path: The path of the file to write to
        """
        # Create the path
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Append file signature if not present
        if path[-5:] != ".limg":
            path += ".limg"

        file = open(path, 'wb')
        file.write(_FILE_SIGNATURE)

        # Write image dimension
        binary_dimension = "{0:016b}{1:016b}".format(self._width, self._height)
        # Split in groups of 8 and convert from binary to base 10
        bytes_array = [int(binary_dimension[i:i+8], 2) for i in range(0, len(binary_dimension), 8)]
        file.write(bytes(bytes_array))

        # TODO write img "mode" or something when implemented

        # Write data to file
        binary_data = ""
        for row in self._data:
            for element in row:
                binary_data += str(element)

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

    def to_array(self) -> List[List[str]]:
        # convert every element into a string to have a uniform export
        return [[str(i) for i in row] for row in self._data]
