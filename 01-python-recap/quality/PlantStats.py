#this module does energy stuff
import os, sys, math
from statistics import *
import json
import csv

DATA = []
TOTAL=0
r = 0.07


def LoadPlants(f = "C:\\Users\\bob\\Desktop\\plants_FINAL_v2.csv"):
    global DATA
    try:
        file = open(f)
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            DATA.append({"name":row[0],"tech":row[1],"cap":eval(row[2]),"gen":eval(row[3]),"capex":eval(row[4]),"opex":eval(row[5]),"life":eval(row[6])})
    except:
        print("something went wrong")
    return DATA


def capacityFactor(plant):
    # capacity in MW, generation in MWh
    cf = plant["gen"] / plant["cap"] * 8760
    return cf


def CF_list(plants):
  l = []
  for i in range(0, len(plants) - 1):
    p = plants[i]
    l.append(p["gen"] / (p["cap"] * 8760))
  return l


def lcoe(p, rate = r):
    """Calculates the capacity factor"""
    costs = p["capex"]
    energy = 0
    for t in range(0, p["life"]):
        costs = costs + p["opex"] / (1 + rate) ** t
        energy = energy + p["gen"] / (1 + rate) ** t
    return costs / energy


def lcoe2(p):
    costs = p["capex"]
    energy = 0
    for t in range(0, p["life"]):
        costs = costs + p["opex"] / (1 + 0.07) ** t
        energy = energy + p["gen"] / (1 + 0.07) ** t
    return costs / energy * 1000


def add_plant(name, tech, cap, gen, capex, opex, life, plants = []):
    plants.append({"name": name, "tech": tech, "cap": cap, "gen": gen, "capex": capex, "opex": opex, "life": life})
    return plants


def do_everything(plants, t, out):
    global TOTAL
    res = {}
    for p in plants:
        if p["tech"] == t or t == None:
            if type(p["cap"]) == int or type(p["cap"]) == float:
                if p["cap"] > 0:
                    if p["life"] > 0:
                        x = lcoe(p)
                        y = p["gen"] / (p["cap"] * 8760)
                        TOTAL = TOTAL + p["gen"]
                        if p["tech"] == "wind":
                            em = 0
                        elif p["tech"] == "solar":
                            em = 0
                        elif p["tech"] == "gas":
                            em = p["gen"] * 0.37
                        elif p["tech"] == "coal":
                            em = p["gen"] * 0.82
                        elif p["tech"] == "Coal":
                            em = p["gen"] * 0.82
                        res[p["name"]] = {"lcoe": x, "cf": y, "em": em}
    if out == True:
        f = open("results.json", "w")
        f.write(json.dumps(res))
    print("Total generation is " + str(TOTAL) + " MWh"); print("done")
    return res


avg = lambda xs: sum(xs) / len(xs)


def best(plants):
    O = None
    for p in plants:
        try:
            if O == None or lcoe(p) < lcoe(O):
                O = p
        except:
            pass
    return O["name"]


if __name__ == "__main__":
    p = LoadPlants(sys.argv[1])
    do_everything(p, None, True)
    print(avg(CF_list(p)))
    print(best(p))
