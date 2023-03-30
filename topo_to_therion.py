# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 01:54:32 2021

@author: alekseyp
"""

import sys, os

rootfile = open(sys.argv[1])

globallines = rootfile.readlines()
globalindex = 0
currentfile = rootfile
output = open("th/megafile.th", "w")
surveys = {"" : ""}
equates = {"" : ""}
currentsurvey = ""
currentdataorder = ["L", "Az", "An"]
planar = False

sys.stdout = open("log.txt", "w")

insurvey = False

def translit_ru_en(l):
    symbols = (u'"`^?абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ',
               u'kt vabvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA')
    tr = {ord(a):ord(b) for a, b in zip(*symbols)}
    return l.translate(tr).strip()


def include_process(l): 
    global globallines, globalindex, currentfile, output, surveys, currentsurvey, insurvey, equates, planar, currentdataorder
    
    filename = l.split()[1]
    
    try: 
        currentfile = open(filename)
    except:
        currentfile = open(os.path.dirname(currentfile.name) + "/" + filename)
        
    globallines[(globalindex + 1) : (globalindex + 1)] = currentfile.readlines()
    
    print(">>INCLUDE FILE " + l.split()[1])
    #surveys[currentsurvey] +="#INCLUDE FILE " + filename + "\n"
    
def survey_process(l):
    global globallines, globalindex, currentfile, output, surveys, currentsurvey, insurvey, equates, planar, currentdataorder
    surveyname = translit_ru_en(l.split()[1]) #+ str(globalindex)
    currentdataorder = ["L", "Az", "An"]
    if not insurvey:
        currentsurvey = surveyname
        if currentsurvey in surveys:
            pass
            #surveys[currentsurvey] += "centerline\n" + "units length meters\n" + "units compass clino degrees\n" + "data normal from to length compass clino\n"
        else:
            equates[currentsurvey] = ""
            surveys[currentsurvey] = "centerline\n" + "units length meters\n" + "units compass clino degrees\n" + "data normal from to length compass clino\n"
        insurvey = True    
    
    
def endsurvey_process(l):
    global globallines, globalindex, currentfile, output, surveys, currentsurvey, insurvey, equates, planar, currentdataorder
    if insurvey:
        insurvey = False
        #surveys[currentsurvey] += "endcenterline\n\n"
        currentsurvey = ""
    
def equate_process(l):
    global globallines, globalindex, currentfile, output, surveys, currentsurvey, insurvey, equates, planar, currentdataorder
    
    command, arg1, arg2 = l.split()[:3]
    
    if arg1[0] == "^":
        arg1 = arg1[1:]    
    if not "." in arg1:
        tharg1 = arg1
    else:
        surv1, st1 = arg1.split(".")[:2]
        tharg1 = st1 + "@" + surv1
    
    if arg2[0] == "^":
        arg2 = arg2[1:]    
    if not "." in arg2:
        tharg2 = arg2
    else:
        surv2, st2 = arg2.split(".")[:2]
        tharg2 = st2 + "@" + surv2
    
    if planar:
        tharg1 = tharg1.replace("@", "_")
        tharg2 = tharg2.replace("@", "_")
        equates[""] += tharg1 + " " + tharg2 + " 0 0 0\n"
        print(equates[""])
    else:
        equates[currentsurvey] += "equate " + tharg1 + " " + tharg2 + "\n"
        print(equates[currentsurvey])
    
def data_order_process(l):
    global globallines, globalindex, currentfile, output, surveys, currentsurvey, insurvey, equates, planar, currentdataorder
    order = l.split()[1:4]
    currentdataorder = order
    print(order)
    #"data normal from to length compass clino\n"
    #L Az An
    #analogs = {"L":"length ", "Az":"compass ", "An":"clino "}
    #outstr = "data normal from to "
    #for item in order:
    #    outstr += analogs[item]
    #if not planar:
    #    surveys[currentsurvey] += outstr + "\n"
    #else:
    #    surveys[""] += outstr + "\n"

command_mapping = {"#include" : include_process, "#survey" : survey_process, "#end_survey" : endsurvey_process, "#equate" : equate_process, "#data_order" : data_order_process}

def data_reorder(parts):
    normal = ["L", "Az", "An"]
    newparts = parts[:5]
    for k in normal:
        newparts[normal.index(k) + 2] = parts[currentdataorder.index(k) + 2]
    return newparts

def general_line_process(l):
    global globallines, globalindex, currentfile, output, surveys, currentsurvey, insurvey, equates, planar, currentdataorder
    
    l = l.replace("%", "#")
    l = l.replace(";", "#")
    if l[0] == "#":
        return
    parts = l.split()
    
    clearedparts = []
    for p in parts:
        if not "#" in p:
            clearedparts.append(p)
            
    if parts[0][0] == "^":
        parts[0] = parts[0].replace("^", "")
        parts.insert(0, "-")
    
    
    if len(clearedparts) < 5 :
        return
    for p in parts[2:]:
        if p == "-":
            p = "0"
    parts = data_reorder(parts)
    parts[0] = translit_ru_en(parts[0])
    parts[1] = translit_ru_en(parts[1])
    if planar :
        if parts[0] != "-":
            parts[0] += "_" + currentsurvey
        if parts[1] != "-":
            parts[1] += "_" + currentsurvey
        surveys[""] += " ".join(parts[:5]) + "\n"
    else:
        surveys[currentsurvey] += " ".join(parts[:5]) + "\n"
    #output.writelines(l + "\n")
    
    
def export_surveys():
    global globallines, globalindex, currentfile, output, surveys, currentsurvey, insurvey, equates, planar, currentdataorder
    
    if not planar:
        for s in surveys:
            if s != "":
                print("exporting survey", s)
                soutput = open("th/" + s + ".th", "w")
                soutput.write("survey " + s + "\n")
                soutput.write(surveys[s])
                soutput.write("endcentreline\n")
                soutput.write(equates[s])
                #print(surveys[s])
                #print("endsurvey")
                soutput.write("endsurvey #" + s + "\n\n")
                soutput.close()
                output.write("input " + s + "\n")
    if planar:
        output.write("survey root\n")
        output.write("centerline\n" + "units length meters\n" + "units compass clino degrees\n" + "data normal from to length compass clino\n")
    output.write(surveys[""])
    output.write(equates[""])
    if planar:
        output.write("endcentreline\n")
        output.write("endsurvey \n")    
        


def procession_step():
    global globallines, globalindex, currentfile, output, surveys, currentsurvey, insurvey, equates, planar, currentdataorder
    
    l = globallines[globalindex].strip()
    
    print("line", globalindex, l)
    
    if not len(l.split()):
        globalindex += 1
        return
    
    if l[0] == "#":
        command = l.split()[0]
        
        if command in command_mapping:
            try:
                command_mapping[command](l)
            except:
                print("error in file:", currentfile.name)
                raise
        else:
            print(">>UNKNOWN COMMAND " + command)
    else:
        general_line_process(l)

    globalindex += 1
    
while globalindex < len(globallines):
    procession_step()
export_surveys()
    
output.close()
rootfile.close()