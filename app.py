from flask import *
import pymysql

app=Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/addmember",methods=["POST", "GET"])
def addmembers():
    if request.method=="GET":
        return render_template("addmembers.html")
    else:
        national_id=request.form["national_id"]
        first_name=request.form["first_name"]
        last_name=request.form["last_name"]
        phone=request.form["phone"]
        email=request.form["email"]
        password=request.form["password"]
        dob=request.form["dob"]    

        #connect to the database
        connection=pymysql.connect(host="localhost",user="root",password="",database="chamadb")

        #we use curse method to execute
        cursor=connection.cursor()

        #SQL querry to save (create nwe record in the database)
        sql="""insert into members(national_id,first_name,last_name,phone,email,password,dob)
        values (%s,%s,%s,%s,%s,%s,%s)
        """

        #replace placeholders
        values=(national_id,first_name,last_name,phone,email,password,dob)

        #execute now
        cursor.execute(sql,values)
        
        #to save data
        connection.commit()
        connection.close()
        return render_template("addmembers.html",message="Member Added Successfully")
        
@app.route("/viewstatement")
def viewstatement():
        #get members records from DB
    connection=pymysql.connect(host="localhost",user="root",password="",database="chamadb")
    cursor=connection.cursor()
    sql="select contribution_id,m.national_id,transaction_ref,date_of_payment, Amount_paid,first_name,last_name,phone from contributions INNER JOIN members as m ON contributions.national_id = m.national_id"
    cursor.execute(sql)
    #fetchall is used to fetch all rows
    contributions=cursor.fetchall()

    return render_template("viewstatement.html", contributions=contributions)

@app.route("/viewloanrepayments")
def loanrepayments():
          #get members records from DB
    connection=pymysql.connect(host="localhost",user="root",password="",database="chamadb")
    cursor=connection.cursor()
    sql="select loan_payment_id, m.national_id,date_of_payment, Amount_paid,loan_balance, method_of_pay,first_name from loan_repayments INNER JOIN members as m ON member_id_paying = m.national_id"
    cursor.execute(sql)
    #fetchall is used to fetch all rows
    loan_repayments=cursor.fetchall()

    return render_template("viewloanrepayments.html",loan_repayments=loan_repayments)

@app.route("/viewchamamembers")
def viewchamamembers():
    #get members records from DB
    connection=pymysql.connect(host="localhost",user="root",password="",database="chamadb")
    cursor=connection.cursor()
    sql="select national_id,first_name,last_name,phone,email,password,dob,created_at from members"
    cursor.execute(sql)
    #fetchall is used to fetch all rows
    members=cursor.fetchall()

    return render_template("viewchamamembers.html",members=members)

@app.route("/loanapplications")
def loanapplications():
    return render_template("viewloanapplications.html")
#RUN THE APP

@app.route("/pay")
def contribute():
    return render_template("contribute.html")

import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth
@app.route('/mpesa_payment', methods=['POST'])
def mpesa_payment():
    if request.method == 'POST':
        # Extract POST Values sent
        amount = request.form['amount']
        phone = request.form['phone']

        # Provide consumer_key and consumer_secret provided by safaricom
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes - Your are given Access
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials" # AUTH URL
        # Provide your consumer_key and consumer_secret
        response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        # Get response as Dictionary
        data = response.json()
        # Retrieve the Provide Token
        # Token allows you to proceed with the transaction
        access_token = "Bearer" + ' ' + data['access_token']

        # GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S') # Current Time
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919' # Passkey(Safaricom Provided)
        business_short_code = "174379" # Test Paybile (Safaricom Provided)
        # Combine above 3 Strings to get data variable
        data = business_short_code + passkey + timestamp
        # Encode to Base64
        encoded = base64.b64encode(data.encode())
        password = encoded.decode()

        # BODY OR PAYLOAD
        payload = {
        "BusinessShortCode": "174379",
        "Password":password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": "1", # use 1 when testing
        "PartyA": phone, # change to your number
        "PartyB": "174379",
        "PhoneNumber": phone,
        "CallBackURL": "https://coding.co.ke/api/confirm.php",
        "AccountReference": "SokoGarden Online",
        "TransactionDesc": "Payments for Products"
        }

        # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
        headers = {
        "Authorization": access_token,
        "Content-Type": "application/json"
        }

        # Specify STK Push Trigger URL
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        # Create a POST Request to above url, providing headers, payload
        # Below triggers an STK Push to the phone number indicated in the payload and the amount.
        response = requests.post(url, json=payload, headers=headers)
        print(response.text) #
        # Give a Response
        return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})

app.run(debug=True)