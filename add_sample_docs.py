from app.core.database import SessionLocal
from app.models.document import Document
from app.rag.vector_store import VectorStore

def clear_and_reload_documents():
    db = SessionLocal()

    print("=" * 60)
    print("CLEARING ALL EXISTING DOCUMENTS")
    print("=" * 60)

    try:
        count = db.query(Document).count()
        print(f"Found {count} existing documents")

        db.query(Document).delete()
        db.commit()
        print(f" Deleted all {count} documents")
    except Exception as e:
        print(f" Error deleting documents: {e}")
        db.rollback()
        return

    print()

    print("=" * 60)
    print("ADDING UPDATED DOCUMENTS")
    print("=" * 60)

    vector_store = VectorStore()
    vector_store.set_db(db)

    documents = [
        {
            "content": """
Hypertension (High Blood Pressure):
Hypertension is a condition where blood pressure in the arteries is persistently elevated.
Normal blood pressure is below 120/80 mmHg.
Stage 1 hypertension: 130-139/80-89 mmHg
Stage 2 hypertension: 140/90 mmHg or higher
Symptoms may include headaches, shortness of breath, or nosebleeds, but often there are no symptoms.
Risk factors include obesity, high salt intake, lack of exercise, stress, and family history.
Treatment includes lifestyle changes (diet, exercise, stress management) and medications like ACE inhibitors, beta-blockers, or diuretics.
            """,
            "metadata": {"source": "hypertension_guide.txt", "topic": "cardiovascular"}
        },
        {
            "content": """
Cardiac Arrest:
Cardiac arrest is a sudden loss of heart function, breathing, and consciousness.
It's usually caused by an electrical disturbance in the heart that disrupts pumping.
Common causes include heart attack, arrhythmia, cardiomyopathy, and heart failure.
Symptoms: Sudden collapse, no pulse, no breathing, loss of consciousness.
Emergency treatment: Immediate CPR and defibrillation are critical.
Prevention includes managing heart disease risk factors, regular checkups, and healthy lifestyle.
            """,
            "metadata": {"source": "cardiac_emergency.txt", "topic": "emergency"}
        },
        {
            "content": """
Diabetes Management:
Type 2 diabetes is a chronic condition affecting how the body processes blood sugar (glucose).
Normal fasting blood sugar: 70-99 mg/dL
Prediabetes: 100-125 mg/dL
Diabetes: 126 mg/dL or higher
Symptoms include increased thirst, frequent urination, fatigue, blurred vision.
Management includes blood sugar monitoring, healthy diet, regular exercise, and medications (metformin, insulin).
Complications can affect heart, kidneys, eyes, and nerves if uncontrolled.
            """,
            "metadata": {"source": "diabetes_info.txt", "topic": "endocrine"}
        },
        {
            "content": """
Heart Attack (Myocardial Infarction):
A heart attack occurs when blood flow to part of the heart is blocked, usually by a blood clot.
Common symptoms: Chest pain or discomfort, pain in arms/back/neck/jaw, shortness of breath, cold sweat, nausea.
Warning signs may appear days or weeks before: unusual fatigue, sleep disturbances, anxiety.
Risk factors: High blood pressure, high cholesterol, smoking, diabetes, obesity, family history.
Treatment: Emergency care (aspirin, nitroglycerin), procedures (angioplasty, stents), medications (blood thinners, beta-blockers).
Recovery includes cardiac rehabilitation, lifestyle changes, and ongoing medication.
            """,
            "metadata": {"source": "heart_attack_guide.txt", "topic": "cardiovascular"}
        },
        {
            "content": """
Cholesterol Management:
Cholesterol is a waxy substance in blood needed for building cells.
LDL (bad cholesterol): Should be below 100 mg/dL (optimal)
HDL (good cholesterol): Should be 60 mg/dL or higher
Total cholesterol: Should be below 200 mg/dL
High cholesterol increases risk of heart disease and stroke.
Management: Healthy diet (low saturated fat), exercise, weight management, and statins if needed.
Foods to eat: Oats, fish, nuts, olive oil, fruits, vegetables.
Foods to avoid: Trans fats, saturated fats, processed meats.
            """,
            "metadata": {"source": "cholesterol_guide.txt", "topic": "cardiovascular"}
        },
        {
            "content": """
About Alfaz:
Born and brought up from kulai,mangalore.
Alfaz is a Engineer working at Boston technology corporation(Bangalore) with months of experience in IT sector .
Specializations: Artificial intelligence and machine learning including python .
Education: 
- completed schooling from Bharati English medium school kulai(2019)
- done my PU education at ST.Aloysius pu college managlore(2019-21)
- BE from Sahyadri college of engineering and management(2021-25)
Current Position: AI-python engineer at Boston technology corporation ,previously worked as AI engineer at Airat systems LLP(NITK).
Languages: English, Hindi, Urdu,Malayalam.
            """,
            "metadata": {"source": "Alfaz_profile.txt", "topic": "profile"}
        },

    ]

    for i, doc in enumerate(documents, 1):
        try:
            vector_store.add_document(
                content=doc["content"],
                metadata=doc["metadata"]
            )
            print(f" Added document {i}: {doc['metadata']['source']}")
        except Exception as e:
            print(f" Error adding document {i}: {e}")

    print()
    print("=" * 60)
    print("DOCUMENT RELOAD COMPLETE!")
    print("=" * 60)

    # Verify
    final_count = db.query(Document).count()
    print(f"Total documents in database: {final_count}")

    db.close()


if __name__ == "__main__":
    print("️  WARNING: This will DELETE all existing documents!")
    print("Are you sure you want to continue? (yes/no): ", end="")

    confirmation = input().strip().lower()

    if confirmation == "yes":
        clear_and_reload_documents()
    else:
        print("Operation cancelled.")