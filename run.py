import json
from os import listdir
from os.path import isfile, join


class ConvertToGeojson:

    def __init__(self):
        pass

    def run_geojson(self):
        self.write_geojson(self.get_file_names("SectorTxtFiles"))

    def read_sector_file(self, file_path: str) -> list:
        output = []
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line == "":
                    continue
                if line[0] in ["N", "E", "S", "W"]:
                    split_line = line.split(' ')
                    lat1, lon1 = self.convert_lat_lon(split_line[0], split_line[1])
                    lat2, lon2 = self.convert_lat_lon(split_line[2], split_line[3])

                    output.append([lon1, lat1])
                    output.append([lon2, lat2])

        # do check
        if self.check_list(output):
            return output
        else:
            print("First Does not match last in:", file_path)
            #output.append(output[0])
            return [[-108.369140625,33.137551192346145],
                     [-107.9736328125,32.287132632616384],
                     [-107.0068359375,33.19273094190692],
                     [-108.369140625,33.137551192346145]]

    @staticmethod
    def check_list(coord_list: list) -> bool:
        first = coord_list[0]
        last = coord_list[-1]
        if first == last:
            return True

    def write_geojson(self, directory: list, write_file: bool = True) -> dict:
        output = {"type": "FeatureCollection",
                  "features": []
                  }

        for file in directory:
            output["features"].append({"type": "Feature",
                                       "properties": self.get_properties(file),
                                       "geometry": {"type": "Polygon",
                                                    "coordinates": [self.read_sector_file(file)]},
                                       })

        if write_file:
            with open("data.json", "w") as outfile:
                json.dump(output, outfile, indent=4)

        return output

    def get_properties(self, filename) -> dict:
        output = {"file_path": filename,
                  "id": "-".join(filename.split('\\')[1].replace(".txt", "").split('_')[1:]),
                  "alt-low": "",
                  "alt-high": "",
                  "alt-range": "",
                  "stroke": "#555555",
                  "stroke-width": 1,
                  "stroke-opacity": 1,
                  "fill": "#940000",
                  "fill-opacity": "0.5",
                  "height": 20,
                  "elevation_m": 60000}

        return output

    @staticmethod
    def convert_lat_lon(lat: str, lon: str) -> tuple:
        original_latitude = lat
        original_longitude = lon

        original_latitude = "-".join(original_latitude.split('.')[0:2]) + "." + original_latitude.split('.')[-1]
        original_longitude = "-".join(original_longitude.split('.')[0:2]) + "." + original_longitude.split('.')[-1]

        latitude = sum(float(x) / 60 ** n for n, x in enumerate(original_latitude[1:].split('-'))) * (
            1 if 'N' in original_latitude[0] else -1)
        longitude = sum(float(x) / 60 ** n for n, x in enumerate(original_longitude[1:].split('-'))) * (
            1 if 'E' in original_longitude[0] else -1)

        return latitude, longitude

    @staticmethod
    def get_file_names(directory: str) -> list:
        only_files = []
        for file in listdir(directory):
            if isfile(join(directory, file)):
                only_files.append(join(directory, file))

        return only_files


if __name__ == '__main__':
    obj = ConvertToGeojson()
    obj.run_geojson()
    #obj.write_kml(json_file_path="C:\\Users\\Pocono Coast West\\Dropbox\\ZLC 4. Facility Engineer\\05_OTHER\\ZLC_Sector_Data.json")
