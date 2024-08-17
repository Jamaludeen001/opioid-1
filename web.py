from flask import Flask, request, render_template, redirect, url_for, session, send_file,flash
import mysql.connector
import csv
import io
import pandas as pd
import numpy as np
import tensorflow as tf
import pickle
from ordinal import Ordinal
from  vectorize import Vectorize
from sklearn.preprocessing import RobustScaler
from pandas_profiling import ProfileReport
import re
import matplotlib.pyplot as plt
import seaborn as sns

plt.ioff()
import matplotlib
matplotlib.use('Agg')



app = Flask(__name__)
app.secret_key = 'my_secret_key'  

ins=[pickle.load(open("instokenizer.pkl", "rb")),"instokenizer.pkl"]
mrg=[pickle.load(open("mrgtokenizer.pkl", "rb")),"mrgtokenizer.pkl"]
diag=[pickle.load(open("diagtokenizer.pkl", "rb")),"diagtokenizer.pkl"]
drg=[pickle.load(open("drgtokenizer.pkl", "rb")),"drgtokenizer.pkl"]
drgnamepoe=[pickle.load(open("drgnptokenizer.pkl", "rb")),"drgnptokenizer.pkl"]
drgnamegeneric=[pickle.load(open("drgngtokenizer.pkl", "rb")),"drgngtokenizer.pkl"]
drgtype=[pickle.load(open("drgttokenizer.pkl", "rb")),"drgttokenizer.pkl"]
model=[pickle.load(open("lstmmodel.pkl", "rb")),"lstmmodel.pkl"]

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1213",
        database="db1"
    )
    return connection

@app.route('/')
def home():
    return redirect(url_for('physician_login'))

@app.route('/physician_login')
def physician_login():
    return render_template('physician_login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
   
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM physicians WHERE username = %s AND password = %s", (username, password))
    physician = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if physician:
        session['username'] = username
        return redirect(url_for('physician_working'))
    else:
        error = "Invalid username or password"
        flash('Entered wrong username or password. Please try again.', 'danger')
        return render_template('physician_login.html', error=error)

@app.route('/physiciansignup',methods=['GET','POST'])
def physiciansignup():
    return render_template("signup.html")


@app.route('/signup',methods=['POST'])
def signup():
    name=request.form['new_username']
    password=request.form['new_password']

    connection=get_db_connection()
    cursor=connection.cursor(dictionary=True)

    cursor.execute("select max(id) from physicians")
    last_id=cursor.fetchall()
    print(last_id)
    new_id=last_id[0]['max(id)']+1
    cursor.execute('''
                INSERT INTO physicians (
                    id,username,password
                ) VALUES (%s, %s,%s)
            ''', (new_id,name,password))
    
    connection.commit()
    cursor.close()
    connection.close()
    flash('You have registered successfully! Login to continue.', 'success')
    
    
    return redirect(url_for('physician_login'))

@app.route('/physician_working', methods=['GET', 'POST'])
def physician_working():
    if 'username' in session:
        username = session['username']
        
        if request.method == 'POST':
            patient_id = request.form['patient_id']
            session['patient_id'] = patient_id
            
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM patients WHERE subject_id = %s ORDER BY admittime", (patient_id,))
            patient = cursor.fetchone()
            
            cursor.fetchall()  
            
            cursor.close()
            connection.close()
            
            if patient:
                return render_template('physician_working.html', username=username, patient=patient)
            else:
                error = "Patient not found"
                return render_template('physician_working.html', username=username, error=error)
        
        return render_template('physician_working.html', username=username)
    else:
        return redirect(url_for('physician_login'))
    
@app.route('/add_new_patient', methods=['GET', 'POST'])
def add_new_data():
    if 'username' in session:
        if request.method == 'POST':
            # Get the form data from the request
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("select max(subject_id) from patients")
            last_id=cursor.fetchall()
           
          
            subject_id=last_id[0][0]+1
            insurance = request.form['insurance']
            marital_status = request.form['marital_status']
            admittime = request.form['admittime']
            dischtime = request.form['dischtime']
            diagnosis = request.form['diagnosis']
            drug_type = request.form['drug_type']
            drug_name_generic = request.form['drug_name_generic']
            dose_val_rx=request.form['dose_val_rx']
            dose_unit_rx= request.form['dose_unit_rx']
            form_val_disp = request.form['form_val_disp']
            form_unit_disp = request.form['form_unit_disp']
            startdate = request.form['startdate']
            enddate = request.form['enddate']
            admission_type=request.form['admission_type']
            hospital_expire_flag=request.form['hospital_expire_flag']

            drug=drug_name_generic
            drug_name_poe=drug_name_generic
            opioid_abuse="no"
            # Connect to the database
            # Insert the new patient data into the patients table
            cursor.execute('''
                INSERT INTO patients (
                    subject_id,admittime,dischtime,admission_type,insurance,marital_status,diagnosis,hospital_expire_flag,startdate,enddate,drug_type,drug,drug_name_poe,drug_name_generic,dose_val_rx,dose_unit_rx,form_val_disp,form_unit_disp,opioid_abuse
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)
            ''', (
                subject_id, admittime,dischtime,admission_type,insurance,marital_status,diagnosis,hospital_expire_flag,startdate,enddate,drug_type,drug,drug_name_poe,drug_name_generic,dose_val_rx,dose_unit_rx,form_val_disp,form_unit_disp,opioid_abuse)
            )

            #Commit the transaction
            connection.commit()

            #Close the connection
            cursor.close()
            connection.close()

            # Redirect to the physician working page after successful data insertion
            return redirect(url_for('physician_working'))
        
        # If the request method is GET, render the form to add a new patient
        return render_template('add_new_patient.html')
    else:
        return redirect(url_for('physician_login'))



@app.route('/patient_history', methods=['GET','POST'])
def patient_history():
    if 'username' in session and 'patient_id' in session:
        patient_id = session['patient_id']
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients WHERE subject_id = %s ORDER BY admittime", (patient_id,))
        history = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        if history:
            return render_template('patient_history.html', history=history)
        else:
            error = "No history found for this patient"
            return render_template('patient_history.html', error=error)
    else:
        return redirect(url_for('physician_login'))

@app.route('/check_risk', methods=['GET'])
def check_risk():
    if 'username' in session and 'patient_id' in session:
        patient_id = session['patient_id']
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients WHERE subject_id = %s ORDER BY admittime", (patient_id,))
        patient_data = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        if patient_data:
            
            csv_output = io.StringIO()
            csv_writer = csv.writer(csv_output)
            csv_writer.writerow(patient_data[0].keys())  
            for row in patient_data:
                csv_writer.writerow(row.values()) 
            
            csv_output.seek(0)
            csv_content = csv_output.getvalue()
            
            df = pd.read_csv(io.StringIO(csv_content))

            sequences = []
            print(df)
            grouped = df.groupby('subject_id')
            for patient_id, group in grouped:
                group = group.sort_values(by='enddate')
                features = group.drop(columns=['subject_id'])
                sequences.append(features)

            for i in sequences:
                print(i.info(),12131214)

            session['sequences'] = [seq.to_csv(index=False) for seq in sequences]

            model=pickle.load(open("lstmmodel.pkl", "rb"))

            preprocessed_df=preprocess(df,model[1],patient_id,1)

            y=model[0].predict(preprocessed_df)

            pred=[]

            for i in y:
                if i>0.8:
                    pred.append("yes")
                else:
                    pred.append("no")
            print(pred)

            dict1={}
            for i in range(1,len(pred)+30):
                dict1[i]=[]
            
            s=1;e=30
            for i in range(0,len(pred)):
                for j in range(s+i,e+i+1):
                    dict1[j].append(pred[i])

            print(dict1)
            for i in range(1,len(pred)+30):
                dict1[i]=dict1[i].count("yes")/len(dict1[i])

            print(dict1)

            session['days_probability']=dict1
            

            #df["opioid_abuse"]=pred
            df=df.sort_values(by="enddateyear")
            data = df.to_html(classes='table table-striped', index=False)

            return redirect(url_for('report'))

            # Send the CSV file as a downloadable file
    else:
        return redirect(url_for('physician_login'))
    


    
def preprocess(df,model_cols,id,flag):

        df["dose_val_rx"]=Ordinal.drug(df,"dose_val_rx")
        df["form_val_disp"]=Ordinal.drug(df,"form_val_disp")

        df["dose_unit_rx"]=Ordinal.medication1(df,"dose_unit_rx")
        df["form_unit_disp"]=Ordinal.medication2(df,"form_unit_disp")

        df["admittimeyear"]=Ordinal.timenormalize(df,"admittime")
        df["dischtimeyear"]=Ordinal.timenormalize(df,"dischtime")

        df["startdateyear"]=Ordinal.timenormalize(df,"startdate")
        df["enddateyear"]=Ordinal.timenormalize(df,"enddate")

        df=columns_vectorize(df,"insurance",ins)
        df=columns_vectorize(df,"marital_status",mrg)
        df=columns_vectorize(df,"diagnosis",diag)
        df=columns_vectorize(df,"drug_type",drgtype)
        df=columns_vectorize(df,"drug",drg)
        df=columns_vectorize(df,"drug_name_poe",drgnamepoe)
        df=columns_vectorize(df,"drug_name_generic",drgnamegeneric)

        df["admdiff"]=df["dischtimeyear"]-df["admittimeyear"]
        df["dosgdiff"]=df["enddateyear"]-df["startdateyear"]
        df=df.drop("opioid_abuse",axis=1)

        if flag:

            preprocessed_df=pd.DataFrame()
            for i in model_cols:
                preprocessed_df[i]=df[i]

            scaler=RobustScaler()
            print(preprocessed_df.info())
            preprocessed_df=scaler.fit_transform(preprocessed_df)

            scaled_df = pd.DataFrame(preprocessed_df, columns=model_cols)
            scaled_df["subject_id"]=[id for i in range(0,len(preprocessed_df))]
            print(scaled_df.info())

            seq=create_sequences(scaled_df,30,1)

            return seq
        return df

@app.route('/report', methods=['GET'])
def report():
    start = request.args.get('start', default=1, type=int)
    end = request.args.get('end', default=30, type=int)
    session['start']=start
    session['end']=end

    lst = [pd.read_csv(io.StringIO(seq)) for seq in session['sequences']]
    days_prob = session['days_probability']
    print(days_prob)
    s = 0
    for i in range(start, end + 1):
        if str(i) in days_prob:
            s += float(days_prob[str(i)])  
    pred_prob = s / (end - start + 1)

    if pred_prob > 0.8:
        risk_message = "The patient is at high risk of opioid addiction. It is strongly recommended to reduce drug dosages and adjust prescriptions accordingly."
    elif pred_prob > 0.5:
        risk_message = "There is no evidence of overdose or addiction, but the patient has been continuously using drugs. Monitoring and review of their drug usage is advised."
    else:
        risk_message = "The patient shows no signs of addiction or misuse. Regular monitoring should continue as part of routine care."

    # Start generating the HTML table
    html_table = f'''
    <html>
    <head>
        <title>Patient Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                color: #333;
            }}
            h1 {{
                text-align: center;
                color: #007BFF;
                margin-bottom: 20px;
            }}
            form {{
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
            }}
            label {{
                font-size: 14px;
                margin-right: 10px;
            }}
            input[type="number"] {{
                padding: 5px;
                margin-right: 10px;
                border-radius: 4px;
                border: 1px solid #ccc;
                font-size: 14px;
                width: 80px;
            }}
            button {{
                padding: 8px 15px;
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }}
            button:hover {{
                background-color: #0056b3;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 12px;
                text-align: left;
                border: 1px solid #ddd;
            }}
            th, td {{
                padding: 8px 12px;
                border: 1px solid #ddd;
            }}
            th {{
                background-color: #007BFF;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #ddd;
            }}
            .table-container {{
                max-height: 300px; /* Adjust as needed */
                overflow-y: auto;
                margin: 0 auto;
                border: 1px solid #ddd;
            }}
        </style>
    </head>
    <body>
        <h1>Patient Report</h1>
        <form action="{url_for('report')}" method="GET">
            <label for="start">Start Entry:</label>
            <input type="number" id="start" name="start" value="{start}" required>
            <label for="end">End Entry:</label>
            <input type="number" id="end" name="end" value="{end}" required>
            <button type="submit"> go </button>
        </form>
        <form action="{url_for('generate_report')}" method="GET" style="text-align: center;">
            <button type="submit">generate report</button>
        </form>

        <form action="{url_for('analyze_history')}" method="GET" style="text-align: center;">
            <button type="submit">analyze_history</button>
        </form>

        <form action="{url_for('analyze_outcomes')}" method="GET" style="text-align: center;">
            <button type="submit">analyze_outcomes</button>
        </form>


        <div class="table-container">
            <table>
                <thead>
                    <tr>
        '''

    columns = ['Time', 'Diagnosis', 'Drug Name', 'Dosage Unit', 'Dosage Drug', 'Dosage Days']
    for col in columns:
        html_table += f'<th>{col}</th>'
    html_table += '''
                    </tr>
                </thead>
                <tbody>
    '''

    for df in lst:
        df = df[start:end]  # Apply the user-defined row slicing
        df['enddate'] = pd.to_datetime(df['enddate'])
        df['startdate'] = pd.to_datetime(df['startdate'])
        df['time'] = df['admittime'] + ' - ' + df['dischtime']
        df['dosagedays'] = (df['enddate'] - df['startdate']).dt.days
        df['form_val_disp'] = Ordinal.drug(df, "form_val_disp")
        df['dosagedrug'] = df['form_val_disp']

        grouped = df.groupby(['time', 'diagnosis', 'drug', 'drug_name_generic', 'form_unit_disp'], as_index=False).agg({
            'dosagedrug': 'sum',
            'dosagedays': 'sum'
        })

        prev_time = ""
        prev_diagnosis = ""
        prev_drugname = ""
        prev_dosageunit = ""

        for index, row in grouped.iterrows():
            html_table += '<tr>'

            # Conditionally merging cells based on previous row's value
            html_table += f'<td>{row["time"]}</td>' if row['time'] != prev_time else '<td></td>'
            html_table += f'<td>{row["diagnosis"]}</td>' if row['diagnosis'] != prev_diagnosis else '<td></td>'
            html_table += f'<td>{row["drug"]}</td>' if row['drug'] != prev_drugname else '<td></td>'
            html_table += f'<td>{row["form_unit_disp"]}</td>' if row['form_unit_disp'] != prev_dosageunit else '<td></td>'
            html_table += f'<td>{row["dosagedrug"]}</td>'
            html_table += f'<td>{row["dosagedays"] + 1}</td>'

            prev_time = row['time']
            prev_diagnosis = row['diagnosis']
            prev_drugname = row['drug']
            prev_dosageunit = row['form_unit_disp']

            html_table += '</tr>'

    html_table += f'''
                </tbody>
            </table>
        </div>
        <p>Days Probability: {pred_prob}</p>
        <p>{risk_message}</p>
    </body>
    </html>
    '''

    return html_table


@app.route('/generate_report', methods=['GET'])
def generate_report():
    start = session['start']
    end = session['end']
    
    lst = [pd.read_csv(io.StringIO(seq)) for seq in session['sequences']]
    days_prob = session['days_probability']
    s = 0
    for i in range(start, end + 1):
        if str(i) in days_prob:
            s += float(days_prob[str(i)])  
    pred_prob = s / (end - start + 1)
    # Fetch data based on start and end
    # For example, fetch data from a database or a data file

    data=lst[0]
    data=data[start:end]
    data['enddate'] = pd.to_datetime(data['enddate'])
    data['startdate'] = pd.to_datetime(data['startdate'])
    data['time'] = data['admittime'] + ' - ' + data['dischtime']
    data['dosagedays'] = (data['enddate'] - data['startdate']).dt.days
    data['form_val_disp'] = Ordinal.drug(data, "form_val_disp")
    data['dosagedrug'] = data['form_val_disp']

    data=data.sort_values(by="enddate")
    data = data.groupby(['admittime','dischtime','time', 'diagnosis', 'drug', 'drug_name_generic', 'form_unit_disp'], as_index=False).agg({
            'dosagedrug': 'sum',
            'dosagedays': 'sum'
        })
    
    opioids = [
    'Morphine', 'Oxycodone', 'Hydrocodone', 'Fentanyl', 'Codeine', 
    'Hydromorphone', 'Methadone', 'Buprenorphine', 'Oxymorphone', 'Meperidine',
    'Tapentadol', 'Tramadol', 'Alfentanil', 'Remifentanil', 'Sufentanil', 
    'Levorphanol', 'Nalbuphine', 'Butorphanol', 'Pentazocine', 'Dihydrocodeine',
    'Loperamide', 'Diphenoxylate', 'Desomorphine', 'Etorphine', 'Naloxone', 
    'Naltrexone', 'Poppy Seeds', 'Pethidine', 'Nalbuphine', 'Bupropion', 
    'Bupivacaine', 'Dextropropoxyphene', 'Methylnaltrexone', 'Oxymetazoline', 
    'Dextromethorphan', 'Clonidine', 'Naloxegol', 'Naltrexone', 'Phenazocine', 
    'Proglumide', 'Furanylfentanyl', 'Acetylfentanyl', 'Carfentanil', 
    'Beta-hydroxyfentanyl', '3-Methylfentanyl', '4-Anilino-N-phenethylpiperidine', 
    'AP-237', 'Norfentanyl', 'Hydroxycodone', 'Oxycodone', 'Ethylmorphine', 
    'Piritramide', 'Alphaprodine', 'Piperidine', 'Anileridine', 'Etorphine', 
    'Diphenoxylate', 'Lofexidine', 'Dextropropoxyphene', 'Methadone Hydrochloride', 
    'Methadone HCl', 'Fentanyl Citrate', 'Hydromorphone Hydrochloride', 
    'Levorphanol Tartrate', 'Buprenorphine Hydrochloride', 'Nalbuphine Hydrochloride', 
    'Butorphanol Tartrate', 'Oxymorphone Hydrochloride', 'Propoxyphene', 
    'Cox-2 inhibitors', 'Suboxone', 'Subutex', 'Embeda', 'Kadian', 'Roxycodone', 
    'Oxecta', 'Zohydro', 'Hysingla ER', 'Oxycontin', 'Fentora', 'Actiq', 
    'Duragesic', 'Sublimaze', 'Sublocade', 'Buprenex', 'Norco', 'Vicodin', 
    'Lorcet', 'Percocet', 'Tylox', 'Dilaudid', 'Exalgo', 'Opana', 'Avinza', 
    'MS Contin', 'OxyIR', 'Belbuca', 'Cassipa', 'Subutex', 'Lofexidine'
    ]

    high_risk=[]
    for i in data["drug"]:
        if i in opioids:
            high_risk.append(i+"opioid drug")

    if high_risk==[]:
        high_risk.append(list(data[data["dosagedays"]==max(data["dosagedays"])]["drug"])[0]+" obtained based on most frequently used")

    max_dosage=data[data["dosagedrug"]==max(data["dosagedrug"])]["drug"] +" "+ str(max(data["dosagedrug"]))+" "+data[data["dosagedrug"]==max(data["dosagedrug"])]["form_unit_disp"]
    max_days=data[data["dosagedays"]==max(data["dosagedays"])]["drug"] + " "+str(max(data["dosagedays"]))+"days"

    # Calculate required values
    
    # Determine risk message
    if pred_prob > 0.8:
        risk_message = "High Risk: The patient is at high risk of opioid addiction. It is strongly recommended to reduce drug dosages and adjust prescriptions accordingly."
    elif pred_prob > 0.5:
        risk_message = "Moderate Risk: No evidence of overdose or addiction, but the patient has been continuously using drugs. Monitoring and review of their drug usage is advised."
    else:
        risk_message = "Low Risk: The patient shows no signs of addiction or misuse. Regular monitoring should continue as part of routine care."
    
    # Prepare the context dictionary
    context = {
        'patientid':session['patient_id'],
        'time':data['time'][0],
        'diagnosis': data['diagnosis'][0],
        'medications': [
            {
                'drugname': list(data["drug"][-5:])[0],
                'unit':list(data["form_unit_disp"][-5:])[0],
                'dosage': list(data["dosagedrug"][-5:])[0],
                'days': list(data["dosagedays"][-5:])[0]+1
                
            },
            {
                'drugname': list(data["drug"][-5:])[1],
                'unit':list(data["form_unit_disp"][-5:])[1],
                'dosage': list(data["dosagedrug"][-5:])[1],
                'days': list(data["dosagedays"][-5:])[1]+1
                
                
            },
            {
               'drugname': list(data["drug"][-5:])[2],
                'unit':list(data["form_unit_disp"][-5:])[2],
                'dosage': list(data["dosagedrug"][-5:])[2],
                'days': list(data["dosagedays"][-5:])[2]+1
                
            }
            # Additional medications can be added dynamically
        ],
        'highest_risk_drug': " ".join(high_risk),
        'max_dosage': list(max_dosage)[0],
        'max_days': list(max_days)[0],
        'days_probability':pred_prob,
        'risk_message': risk_message,
        'additional_recommendation': " ",
        'provider_name': "OPISAFE",
        'provider_contact': " "
    }
    
    return render_template('report.html', **context)

@app.route('/analyze_history',methods=['GET','POST'])
def analyze_history():
    if 'username' in session and 'patient_id' in session:
        patient_id = session['patient_id']
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients WHERE subject_id = %s ORDER BY admittime", (patient_id,))
        patient_data = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        if patient_data:
            
            csv_output = io.StringIO()
            csv_writer = csv.writer(csv_output)
            csv_writer.writerow(patient_data[0].keys())  
            for row in patient_data:
                csv_writer.writerow(row.values()) 
            
            csv_output.seek(0)
            csv_content = csv_output.getvalue()
            
            df = pd.read_csv(io.StringIO(csv_content))

            profile = ProfileReport(df, title="Pandas Profiling Report", html={"style": {"full_width": True}})
            profile.to_file("templates/history_report.html") 

            return render_template("history_report.html")
        
@app.route('/analyze_outcomes',methods=['GET','POST'])
def analyze_outcomes():
    if 'username' in session and 'patient_id' in session:
        patient_id = session['patient_id']
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients WHERE subject_id = %s ORDER BY admittime", (patient_id,))
        patient_data = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        if patient_data:
            
            csv_output = io.StringIO()
            csv_writer = csv.writer(csv_output)
            csv_writer.writerow(patient_data[0].keys())  
            for row in patient_data:
                csv_writer.writerow(row.values()) 
            
            csv_output.seek(0)
            csv_content = csv_output.getvalue()
            
            df = pd.read_csv(io.StringIO(csv_content))
            p=session["days_probability"]
            k=[int(i) for i in list(p.keys())]
            k.sort()
            k=[str(i) for i in k]
            prob=[]
            for i in k:
                prob.append(p[i])

            print(df.info())
            print(df.index)

            df["endddate"]=pd.to_datetime(df["enddate"])
            df=df.sort_values(by="enddate")

            grouped=df.groupby("enddate")
            timedata=pd.DataFrame()
            t=[];e=[];o=[]
            s=0
            for date,group in grouped:
                t.append(date)
                s=s+len(group)
                e.append(s)
                o.append(sum(prob[:s])/s)
            timedata["time"]=t
            timedata["entry"]=e
            timedata["opioid_strength"]=o
            timedata.index=timedata["entry"]

            entrydata=pd.DataFrame()
            entrydata["entry"]=k
            entrydata["opioid_strength"]=prob
            entrydata.index=entrydata["entry"]

            print(timedata)
            plt.figure(figsize=(26, 6))
            plt.plot(entrydata.loc[:,"opioid_strength"],marker=".",linewidth=0.5,label="each entry")
            plt.plot(timedata.loc[:,"opioid_strength"],marker="o",label="daily")
            plt.legend()
            plt.ylabel("opioid_strength")
            plt.xlabel("entries")
            plt.grid(True)
            plt.savefig('static/line_plot.png')  # Save the plot image in the static directory
            plt.close()

            profile = ProfileReport(df, title="Pandas Profiling Report", html={"style": {"full_width": True}})
            profile.to_file("templates/outcome_report.html") 

            with open('templates/outcome_report.html', 'r') as file:
                html_content = file.read()

    # Create an HTML img tag for the plot
            img_tag = f'<img src="static/line_plot.png" alt="Line Plot" style="display: block; margin: 0 auto;">'

    # Insert the img tag at the very beginning of the <body> tag
    # Ensure you handle the case where <body> tag might have attributes
            html_content = re.sub(r'<body[^>]*>', f'<body>\n{img_tag}', html_content)

    # Write the updated HTML content back to the file
            with open('templates/outcome_report.html', 'w') as file:
                file.write(html_content)

            print(len(p),k)
            

            return render_template("outcome_report.html")



def create_sequences(df, sequence_length,flag):
    sequences = []
    print(df) 
    grouped = df.groupby('subject_id')
    for patient_id, group in grouped:
        if flag:
            group = group.sort_values(by='enddateyear')
        else:
            group = group.sort_values(by='enddate')

        features = group.drop(columns=['subject_id']).values
        for i in range(len(features) - sequence_length):
            sequences.append(features[i:i + sequence_length])

    return np.array(sequences)


def columns_vectorize(df,cols,tokenizer):

    col=Vectorize(df[cols],tokenizer)
    col_word_index,col_tokenize,col_tokens=col.tokenize()
    col_padded=col.padding()
    col.embedding()
    col_model=col.train()
    col_model=col.padded_embedding()
    col_vectorized=col_model.predict(col_padded)

    V1=[];V2=[];V3=[]
    sv1=cols+"v1"
    sv2=cols+"v2"
    sv3=cols+"v3"
    for i in col_vectorized:
        V1.append(i[0])
        V2.append(i[1])
        V3.append(i[2])
    df[sv1]=V1
    df[sv2]=V2
    df[sv3]=V3
    df=df.drop(cols,axis=1)
    return df
    


if __name__ == '__main__':
    app.run(debug=True)
