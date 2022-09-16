from turtle import *
import csv

with open("test2.csv", "w", newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    begin_fill()
    speed(0)
    while True:
        forward(200)
        left(111)
        csv_writer.writerow(["FW200"])
        csv_writer.writerow(["LR111"])
        if abs(pos()) < 1:
            break
    