from app.core.database import SessionLocal
from app.models.document import Document
from app.rag.vector_store import VectorStore

def clear_and_add_test_hospital():
    db = SessionLocal()

    print("=" * 60)
    print("CLEARING ALL EXISTING DOCUMENTS")
    print("=" * 60)

    try:
        count = db.query(Document).count()
        print(f"Found {count} existing documents")

        db.query(Document).delete()
        db.commit()
        print(f"Deleted all {count} documents")
    except Exception as e:
        print(f"Error deleting documents: {e}")
        db.rollback()
        return

    print()
    print("=" * 60)
    print("ADDING TEST HOSPITAL DATA (FICTIONAL - LLM WON'T KNOW THIS)")
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
Symptoms may include headaches, shortness of breath, or nosebleeds.
Risk factors include obesity, high salt intake, lack of exercise, stress, and family history.
Treatment includes lifestyle changes and medications like ACE inhibitors, beta-blockers, or diuretics.
            """,
            "metadata": {"source": "hypertension_guide.txt", "topic": "medical"}
        },
        {
            "content": """
About MediCare Elite Hospital Bangalore:

MediCare Elite Hospital is a fictional premium healthcare facility located at Electronic City Phase 2, Bangalore.

FICTIONAL DATA - THIS IS NOT A REAL HOSPITAL:

Establishment: Founded in January 2025
Address: Plot 42, Sector 7, Electronic City Phase 2, Bangalore - 560100
Contact: +91-80-4567-8900
Email: contact@medicareelite.in

Specializations:
- Cardiology Department headed by Dr. Rajesh Kumar (20 years experience)
- Neurology Department headed by Dr. Priya Sharma (15 years experience)  
- Orthopedics headed by Dr. Amit Patel (18 years experience)

Facilities:
- 24/7 Emergency with air-conditioned ambulances
- 150-bed capacity including 30 ICU beds
- 5 state-of-the-art operation theatres
- In-house pharmacy and diagnostic center
- Free WiFi for all patients

Unique Features:
- First hospital in Bangalore with AI-powered diagnosis system
- Rooftop helipad for emergency air ambulance
- Dedicated COVID-19 isolation ward with 25 beds
- Mobile app "MediCare Connect" for appointment booking

Awards (Fictional):
- Best New Hospital 2025 by Bangalore Medical Association
- Excellence in Patient Care Award 2025
- Green Hospital Certification 2025
            """,
            "metadata": {"source": "medicare_elite_hospital.txt", "topic": "hospital"}
        },
        {
            "content": """
MediCare Elite Hospital - Department of Cardiology:

FICTIONAL CARDIOLOGY DEPARTMENT DETAILS:

Head of Department: Dr. Rajesh Kumar, MD, DM (Cardiology)
- 20 years of experience in interventional cardiology
- Trained at Johns Hopkins Hospital, USA
- Performed over 5,000 angioplasty procedures
- Specializes in complex coronary interventions

Department Statistics (2025):
- 500+ cardiac procedures performed monthly
- 95% success rate in emergency angioplasty
- Average waiting time for OPD: 30 minutes
- Emergency response time: Under 10 minutes

Equipment (Fictional):
- Latest Siemens Artis Zee Cath Lab with AI assistance
- 3D Echocardiography machines (2 units)
- Cardiac CT Scanner - GE Revolution 256-slice
- 24/7 ECG monitoring in all cardiac beds

Special Programs:
- Free heart health checkup every Sunday from 9 AM - 12 PM
- Cardiac rehabilitation program with 6-month follow-up
- School heart screening program (screening 500+ students monthly)
- Diabetes-Heart Disease Management Clinic (Wednesdays)

Consultation Timings:
Dr. Rajesh Kumar: Monday to Friday, 10 AM - 1 PM, 4 PM - 7 PM
Dr. Anita Desai (Associate): Monday to Saturday, 9 AM - 2 PM
Emergency Cardiology: 24/7 with on-call cardiologist

Consultation Fees:
- First consultation: ₹800
- Follow-up: ₹500
- Emergency consultation: ₹1,500
            """,
            "metadata": {"source": "medicare_cardiology.txt", "topic": "hospital"}
        },
        {
            "content": """
MediCare Elite Hospital - Patient Services & Appointment System:

ONLINE APPOINTMENT BOOKING:
Book through our app "MediCare Connect" (Available on Play Store and App Store)
- Select department and doctor
- Choose preferred time slot
- Pay ₹200 booking fee online
- Get instant confirmation SMS
- Receive reminder notification 1 hour before appointment

WALK-IN REGISTRATION:
Reception Counter: Ground Floor
Timing: 8 AM - 8 PM
Token system for walk-in patients
Average wait time: 45 minutes

EMERGENCY SERVICES:
24/7 Emergency Department
Direct admission without appointment for emergencies
Air-conditioned ambulance with cardiac monitor
Emergency hotline: +91-80-4567-9911

HEALTH PACKAGES (Fictional Pricing):
Basic Health Checkup: ₹2,999
- Complete Blood Count
- Lipid Profile  
- Blood Sugar
- ECG
- Doctor Consultation

Cardiac Health Package: ₹5,999
- All Basic tests
- 2D Echo
- TMT (Treadmill Test)
- Cardiologist Consultation
- Diet Chart

Diabetes Management Package: ₹4,499
- HbA1c
- Kidney Function Test
- Eye Checkup
- Endocrinologist Consultation
- Diabetic Diet Plan

INSURANCE ACCEPTED:
- All major health insurance companies
- Cashless facility available
- Ayushman Bharat accepted
- Karnataka Arogya scheme accepted
- International insurance through Third Party Administrator (TPA)

PAYMENT OPTIONS:
- Cash, Card (Credit/Debit)
- UPI, Net Banking
- Medical loans available through Bajaj Finserv
- EMI options for surgeries above ₹50,000
            """,
            "metadata": {"source": "medicare_services.txt", "topic": "hospital"}
        }
    ]

    for i, doc in enumerate(documents, 1):
        try:
            vector_store.add_document(
                content=doc["content"],
                metadata=doc["metadata"]
            )
            print(f"Added document {i}: {doc['metadata']['source']}")
        except Exception as e:
            print(f" Error adding document {i}: {e}")

    db.close()


if __name__ == "__main__":
    print("WARNING: This will DELETE all existing documents!")
    print("This adds FICTIONAL hospital data to prove RAG is working.")
    print("Are you sure you want to continue? (yes/no): ", end="")

    confirmation = input().strip().lower()

    if confirmation == "yes":
        clear_and_add_test_hospital()
    else:
        print("Operation cancelled.")