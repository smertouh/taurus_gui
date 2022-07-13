import json
import os
if os.path.isfile("data_file.json"):
    with open("data_file.json", "r") as read_file:
        MainDict = json.load(read_file)
else:
    MainDict = {}
    MainDict.update({"window_name": "Trend_name"})
    MainDict.update({"Y_axis": [-250, 250, "linear"]})  # linear,log
    list_of_models = []
    dict_of_model = {}
    dict_of_model.update({"model": "eval:a=10;b={tango/test/1/double_scalar}.magnitude*1.667-11.46;a**((b+250)/500)"})
    dict_of_model.update({"name": "vac"})
    dict_of_model.update({"color": "y"})
    dict_of_model.update({"width": 2})
    list_of_models.append(dict_of_model)
    dict_of_model = {}
    dict_of_model.update({"model": "eval:{tango/test/1/double_scalar}.magnitude"})
    dict_of_model.update({"name": "temperature"})
    dict_of_model.update({"color": "r"})
    dict_of_model.update({"width": 4})
    list_of_models.append(dict_of_model)
    MainDict.update({"Models": list_of_models})


with open("data_file.json", "w") as write_file:
    json.dump(MainDict, write_file, indent=4)

with open("data_file.json", "r") as read_file:
    MainDict2 = json.load(read_file)

print(1)