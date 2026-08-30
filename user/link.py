import os
import warnings
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Hide unnecessary sklearn warnings to keep your chat interface perfectly clean
warnings.filterwarnings("ignore", category=UserWarning)

# =====================================================================
# 🛠️ GLOBAL CONFIGURATION PATHS
# =====================================================================
INPUT_KAGGLE_CSV_PATH = r"C:\Users\LSESH\OneDrive\Desktop\archive\Training.csv"
SAVED_MODEL_PATH = "disease_predict_model.pkl"
SAVED_FEATURES_PATH = "symptom_features_list.pkl"


# =====================================================================
# 🪵 SECTION 1: MODEL TRAINING PIPELINE
# =====================================================================
def train_and_save_ai_model():
    if not os.path.exists(INPUT_KAGGLE_CSV_PATH):
        print(f"❌ Error: Cannot find your Kaggle dataset at '{INPUT_KAGGLE_CSV_PATH}'.")
        return False

    print(f"📦 Loading your Kaggle data from: {INPUT_KAGGLE_CSV_PATH}")
    df = pd.read_csv(INPUT_KAGGLE_CSV_PATH)

    # Wipe clean any broken columns generated during Kaggle's packaging sequence
    if "Unnamed: 133" in df.columns:
        df = df.drop(columns=["Unnamed: 133"])

    # Dynamic target column selector
    target_column = None
    possible_names = ["disease", "prognosis", "target", "label", "prognosis_text"]
    for col in df.columns:
        if col.lower().strip() in possible_names:
            target_column = col
            break
    if not target_column:
        target_column = df.columns[-1]

    print(f"🎯 Auto-detected your target disease column as: '{target_column}'")

    symptom_features = [col for col in df.columns if col != target_column]
    
    X = df[symptom_features]        
    y = df[target_column]           

    print(f"⚙️ Training Random Forest Model using {len(symptom_features)} symptoms...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    joblib.dump(model, SAVED_MODEL_PATH)
    joblib.dump(symptom_features, SAVED_FEATURES_PATH)
    print("🎉 AI Engine trained successfully!\n")
    return True


# =====================================================================
# 📝 SECTION 2: INTELLIGENT TEXT PREDICTION ENGINE 
# =====================================================================
def predict_disease_from_text(user_description_text):
    if not os.path.exists(SAVED_MODEL_PATH) or not os.path.exists(SAVED_FEATURES_PATH):
        success = train_and_save_ai_model()
        if not success: return

    model = joblib.load(SAVED_MODEL_PATH)
    symptom_features = joblib.load(SAVED_FEATURES_PATH)

    clean_sentence = user_description_text.lower()
    binary_vector = np.zeros(len(symptom_features))

    # 🗺️ HUMAN SYMPTOM SYNONYM MATRIX MAPPING
    # This translates common casual human text phrases straight to your Kaggle columns
    synonyms = {
        "cold": ["continuous_sneezing", "runny_nose", "throat_irritation"],
        "sneezing": ["continuous_sneezing"],
        "sniffles": ["runny_nose"],
        "cough": ["cough"],
        "coughing": ["cough"],
        "fever": ["high_fever"],
        "feverish": ["high_fever"],
        "shivering": ["shivering"],
        "chills": ["chills"],
        "headache": ["headache"],
        "head hurt": ["headache"],
        "stomach ache": ["stomach_pain"],
        "stomach hurts": ["stomach_pain"],
        "vomit": ["vomiting"],
        "vomiting": ["vomiting"],
        "throwing up": ["vomiting"],
        "nausea": ["vomiting"],
        "loose motion": ["diarrhoea"],
        "diorrhea": ["diarrhoea"],
        "diarrhea": ["diarrhoea"],
        "fatigue": ["fatigue"],
        "tired": ["fatigue"],
        "weakness": ["fatigue"],
        "itching": ["itching"],
        "itchy": ["itching"],
        "rash": ["skin_rash"]
    }

    # Step A: Scan custom conversational human shortcuts matrix
    for human_word, kaggle_columns in synonyms.items():
        if human_word in clean_sentence:
            for col in kaggle_columns:
                if col in symptom_features:
                    idx = symptom_features.index(col)
                    binary_vector[idx] = 1

    # Step B: Backup loop scanner matching column strings cleanly
    for index, symptom in enumerate(symptom_features):
        clean_symptom_name = symptom.lower().replace("_", " ").strip()
        if clean_symptom_name in clean_sentence:
            binary_vector[index] = 1

    # Convert mapping matrix array to DataFrame to silence training context warnings
    processed_input_df = pd.DataFrame([binary_vector], columns=symptom_features)
    
    probabilities = model.predict_proba(processed_input_df)[0]
    disease_classes = model.classes_

    print("\n-------------------------------------------")
    print("🔮 DIAGNOSIS PREDICTION MATRIX:")
    print("-------------------------------------------")
    
    has_matches = False
    results = sorted(zip(disease_classes, probabilities), key=lambda x: x[1], reverse=True)
    
    for disease, prob in results:
        percentage = prob * 100
        # Only output diseases with > 5% prediction confidence to clear system noise
        if percentage > 5.0:  
            print(f"🎯 {disease}: {percentage:.1f}%")
            has_matches = True
            
    if not has_matches:
        print("⚠️ No matching symptoms identified in your text description.")
    print("-------------------------------------------\n")


# =====================================================================
# 🚀 INTERACTIVE CHAT LOOP INTERFACE
# =====================================================================
if __name__ == "__main__":
    # Check if we need to run first-time initialization training sequences
    if not os.path.exists(SAVED_MODEL_PATH) or not os.path.exists(SAVED_FEATURES_PATH):
        print("🤖 Initializing AI engine database configurations...")
        train_and_save_ai_model()
    else:
        print("🤖 Loaded existing saved AI model assets smoothly.\n")

    print("==================================================")
    print("      Welcome to the Foodie Disease Chat System     ")
    print("==================================================")
    print("Type out your symptoms naturally to test the AI.")
    print("Type 'exit' or 'quit' to close the program, yar.\n")

    # Infinite interactive prompt processing engine loop
    while True:
        user_input = input("💬 Describe your symptoms: ")
        
        if user_input.strip().lower() in ['exit', 'quit']:
            print("👋 Closing chat simulator. Goodbye, yar!")
            break
            
        if not user_input.strip():
            continue
            
        predict_disease_from_text(user_input)