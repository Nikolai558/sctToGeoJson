import json
from os import listdir
from os.path import isfile, join


class ConvertToGeojson:

    def __init__(self):
        self.write_file = True
        self.sct_file_dir = "SctFiles"
        self.altitude = "altitudes.json"
        self.geo_json = None
        self.run_geojson()

    def run_geojson(self):
        self.write_geojson(self.get_file_names())

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
            print(f"{file_path}\n\tThis File has coordinates that are incorrect."
                  f"\n\tThe first and last coordinates have to be the same.")
            return [[]]

    def write_geojson(self, directory: list) -> dict:
        output = {"type": "FeatureCollection",
                  "features": []
                  }

        for file in directory:
            add_feature = {"type": "Feature",
                           "properties": self.get_properties(file),
                           "geometry": {"type": "Polygon",
                                        "coordinates": [self.read_sector_file(file)]
                                        }
                           }
            if add_feature["geometry"]["coordinates"] != [[[]]]:
                output["features"].append(add_feature)

        if self.write_file:
            with open("data.json", "w") as outfile:
                json.dump(output, outfile, indent=4)
        self.geo_json = output

        return output

    def get_file_names(self) -> list:
        only_files = []
        for file in listdir(self.sct_file_dir):
            if isfile(join(self.sct_file_dir, file)):
                only_files.append(join(self.sct_file_dir, file))

        return only_files

    def get_properties(self, filename) -> dict:
        sector_id = "-".join(filename.split('\\')[1].replace(".txt", "").split('_')[1:])
        alt_high = ""
        alt_low = ""

        try:
            with open(self.altitude, "r") as file:
                artcc_sector_altitudes = json.load(file)
                alt_high = artcc_sector_altitudes[sector_id.split('-')[0]][sector_id]["high"]
                alt_low = artcc_sector_altitudes[sector_id.split('-')[0]][sector_id]["low"]
        except KeyError as e:
            print(f"Key Error: Can NOT assign ALT limits for {e}")
        except FileNotFoundError as e:
            print(f"File Not Found Error: {e}")
            exit(1)

        output = {"id": sector_id,
                  "alt-low": alt_low,
                  "alt-high": alt_high,
                  "stroke": "#555555",
                  "stroke-width": 1,
                  "stroke-opacity": 1,
                  "fill": "#940000",
                  "fill-opacity": "0.5"}

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
    def check_list(coord_list: list) -> bool:
        first = coord_list[0]
        last = coord_list[-1]
        if first == last:
            return True


if __name__ == '__main__':
    obj = ConvertToGeojson()
