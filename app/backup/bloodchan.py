from flask import Flask, jsonify, request, render_template
import csv
import requests
import pandas as pd


app = Flask(__name__)

types = [{'bloodtype': 'O+' , 'matches': ["O-", "O+"]},
{'bloodtype': 'A+' , 'matches': ['O-', 'O+', 'A-', 'AB-']},
{'bloodtype': 'B+' , 'matches': ['O-','O+', 'B-', 'B+']},
{'bloodtype': 'AB+' , 'matches': ['O-', 'O+', 'B-','B+', 'A-', 'A+', 'AB-', 'AB+']},
{'bloodtype': 'O-' , 'matches': ['O-']},
{'bloodtype': 'A-' , 'matches': ['O-','A-']},
{'bloodtype': 'B-' , 'matches': ['O-', 'B-']},
{'bloodtype': 'AB-' , 'matches': ['O-', 'B-', 'A-', 'AB-']}
]


def open_file(file_name):
    list = []
    with open(file_name) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            list.append(row)
    return list


@app.route("/", methods=["POST", "GET"])
def home():
    return render_template("home.html")

@app.route("/calculator", methods=["POST", "GET"])
def form():
    return render_template("form.html")

@app.route("/result", methods=["POST", "GET"])
def confirm():
    donor = []
    confirmation = request.form['blood'].upper()
    list_1 = ""
    for type in types:
        if confirmation == type['bloodtype']:
            donor.append(type['matches'])
            list_2 = donor[0].pop(-1)
    for d in donor[0]:
        list_1 += d
        list_1 += ", "
    list_1 = list_1[:-2]
    return render_template("Index.html", message_1= confirmation, message_2 = list_1)


@app.route("/inventory", methods=["POST", "GET"])
def stock_search():
    table  = pd.read_csv('stock.csv')
    return render_template("stockform.html", table=table.values )

@app.route("/inventoryresult", methods=["POST", "GET"])
def stock_result():
    table  = pd.read_csv('stock.csv')
    list = open_file('stock.csv')
    confirmation =  request.form['blood'].upper()
    for l in list:
        if confirmation == l["Type"]:
            stockresult ="We have "+l["Stock"]+" of Type "+ l["Type"]+ " in stock."
    return render_template("stockindex.html", message_1 = stockresult, table=table.values)

@app.route("/transfusion", methods=["POST", "GET"])
def patient_search():
    table  = pd.read_csv("patient.csv")
    return render_template("transfusionform.html", table=table.values  )


@app.route("/transfusionresult", methods=["POST", "GET"])
def transfusion():
    confirmation =  request.form['blood']
    stock_match = ""
    transfusion_list = open_file('patient.csv')
    for t in transfusion_list:
        if t["Patient"] == confirmation:
            patient_result = t["Patient"]+" is "+ t["Blood Type"]
            stock_match = t["Blood Type"]
    list = open_file('stock.csv')
    for l in list:
        if l["Type"] == stock_match:
            match_result = "We have "+l["Stock"]+" in stock"
    table  = pd.read_csv("patient.csv")
    return render_template("transfusionindex.html", message_1 = patient_result, message_2 = match_result, table=table.values )

@app.route("/login", methods=["POST", "GET"])
def login():
    return render_template("loginform.html")


@app.route("/temp", methods=["POST", "GET"])
def temp():
    if not "user" in request.form:
        return render_template("loginform.html")
    username =  request.form['user']
    password =  request.form['pass']
    table  = pd.read_csv("patient.csv")
    list = open_file('logins.csv')
    for l in list:
        if l['username'] == username and l['password'] == password:
            return render_template("book_patient.html", table=table.values )

@app.route("/order", methods=["POST", "GET"])
def order():
    return render_template("loginform.html")

@app.route("/order/book", methods=["POST", "GET"])
def book():

        stocklist  = []
        noorderlist =[]
        insufficient_stock = []
        newlist = []
        poplist =[]
        superlist = []
        postlist =[]

        for patientid in request.form:
            qty = request.form[patientid]
            id = patientid.split('_')[1]
            blood = patientid.split('_')[2]
            orderdic = {"PatientID" : id, "Order" : qty, "Blood" : blood}


            list = open_file("Stock.csv")
            for l in list:
                if l["Type"] == orderdic["Blood"] and int(l['Stock']) >= int(orderdic['Order']):
                    super = {"PatientID" :id, "Order" : qty, "Blood" : blood, "Stock" : l["Stock"]}
                    superlist.append(super)
                    poplist.append(id)
                    l["Stock"] = int(l["Stock"]) - int(qty)
                    stocklist.append(l)
                    noorderlist.append(l["Type"])
                elif l["Type"] == orderdic["Blood"] and l['Stock'] < orderdic['Order']:
                    insufficient = {"PatientID" : id, "Blood" : blood, "Order" : qty,"Stock" : l["Stock"]}
                    insufficient_stock.append(insufficient)



        list = open_file("Stock.csv")
        for l in list:
            if l["Type"] not in noorderlist:
                stocklist.append(l)

        with open('stock.csv', 'w', newline='') as csvfile:
            fieldnames = ['Type', 'Stock']
            stocker = csv.DictWriter(csvfile, fieldnames=fieldnames)
            stocker.writeheader()
            for d in stocklist:
                stocker.writerow(d)

        list = open_file('patient.csv')
        for l in list:
            if l["PatientID"] in poplist:
                newlist.append(l)

        list = open_file('patient.csv')
        for l in list:
            if l["PatientID"] not in poplist:
                postlist.append(l)



        with open('booked_patient.csv', 'w', newline='') as csvfile:#
            fieldnames = ['PatientID', 'Blood', 'Order']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(orderdic)

        with open('confirmed.csv', 'w', newline='') as csvfile:#
            fieldnames = ['PatientID', 'Blood', 'Order', 'Stock']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for s in superlist:
                writer.writerow(s)

        with open('backlog.csv', 'w', newline='') as csvfile:
            fieldnames = ['PatientID', "Order","Blood", "Stock"]
            backloger = csv.DictWriter(csvfile, fieldnames=fieldnames)
            backloger.writeheader()
            for d in insufficient_stock:
                backloger.writerow(d)

        with open('patient.csv', 'w', newline='') as csvfile:
            fieldnames = ['Patient', 'PatientID', "DOB", "Blood Type", "Order"]
            patienter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            patienter.writeheader()
            for d in postlist:
                patienter.writerow(d)

        table  = pd.read_csv("confirmed.csv")
        table2  = pd.read_csv("backlog.csv")

        return render_template("orderindex0.html", message_1 = "", table=table.values, table2= table2.values)




@app.route("/order/book/booked", methods=["POST", "GET"])
def booked():#
    table  = pd.read_csv('booked_patient.csv')
    table2  = pd.read_csv("backlog.csv")

    return render_template("orderindex0.html", message_1 = "", table=table.values, table2= table2.values )


if __name__ == "__main__":
    app.run(debug = True)
