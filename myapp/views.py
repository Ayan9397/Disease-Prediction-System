from django.shortcuts import render, redirect
from django.db import connection  # NEW: Import this to run a direct database command
import os
import joblib
import pandas as pd
from .models import History

# Load the trained model and label encoder
path = os.path.dirname(__file__)
model = joblib.load(open(os.path.join(path, 'best_model.pkl'), 'rb'))
label_encoder = joblib.load(open(os.path.join(path, 'label_encoder.pkl'), 'rb'))

# List of symptoms the model expects
SYMPTOM_COLUMNS = [
    'fever', 'headache', 'nausea', 'vomiting', 'fatigue', 
    'joint_pain', 'skin_rash', 'cough', 'weight_loss', 'yellow_eyes'
]

# --- VIEWS ---

def home(req):
    """Renders the new detailed homepage."""
    return render(req, 'myapp/home.html')

def symptom_checker(req):
    """Handles both displaying the form and processing the prediction."""
    if req.method == 'POST':
        user_input = [1 if req.POST.get(symptom) else 0 for symptom in SYMPTOM_COLUMNS]
        input_df = pd.DataFrame([user_input], columns=SYMPTOM_COLUMNS)
        
        result = model.predict(input_df)[0]
        res = label_encoder.inverse_transform([result])[0]
        
        history_data = {symptom: value for symptom, value in zip(SYMPTOM_COLUMNS, user_input)}
        history_data['res'] = res
        
        his = History(**history_data)
        his.save()

        symptoms_for_template = []
        for symptom in SYMPTOM_COLUMNS:
            symptoms_for_template.append({
                'name': symptom,
                'checked': history_data.get(symptom) == 1
            })

        context = {
            'res': res,
            'symptoms': symptoms_for_template
        }
        return render(req, 'myapp/symptom_checker.html', context)
    
    # For a GET request, just display the form
    symptoms_for_template = [{'name': s, 'checked': False} for s in SYMPTOM_COLUMNS]
    context = {'symptoms': symptoms_for_template}
    return render(req, 'myapp/symptom_checker.html', context)

def history(req):
    """Displays all past prediction records."""
    his = History.objects.all().order_by('id')
    return render(req, 'myapp/history.html', {'his': his})

def clear_history(req):
    """Deletes all records and resets the ID counter."""
    if req.method == 'POST':
        # First, delete all the objects from the table
        History.objects.all().delete()
        
        # NEW: Reset the auto-increment counter for the 'myapp_history' table
        with connection.cursor() as cursor:
            cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'myapp_history'")
            
    return redirect('history')