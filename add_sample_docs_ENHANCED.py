from app.core.database import SessionLocal
from app.models.document import Document
from app.rag.vector_store import VectorStore
from app.rag.chunker import chunk_document


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
    print("ADDING TEST HOSPITAL DATA WITH CHUNKING")
    print("=" * 60)

    vector_store = VectorStore()
    vector_store.set_db(db)

    # Expanded documents with more medical content
    documents = [
        {
            "content": """Hypertension (High Blood Pressure):
Hypertension is a condition where blood pressure in the arteries is persistently elevated.
Normal blood pressure is below 120/80 mmHg.
Stage 1 hypertension: 130-139/80-89 mmHg.
Stage 2 hypertension: 140/90 mmHg or higher.
Symptoms may include headaches, shortness of breath, or nosebleeds.
Risk factors include obesity, high salt intake, lack of exercise, stress, and family history.
Treatment includes lifestyle changes and medications like ACE inhibitors, beta-blockers, or diuretics.
Prevention involves regular exercise, reducing salt intake, managing stress, and maintaining healthy weight.
Complications of untreated hypertension include heart disease, stroke, kidney damage, and vision problems.
Regular blood pressure monitoring is essential for early detection and management.""",
            "metadata": {"source": "hypertension_guide.txt", "topic": "medical"}
        },
        {
            "content": """Diabetes Mellitus - Types and Management:
Diabetes is a metabolic disorder characterized by elevated blood glucose levels.
Type 1 Diabetes: Autoimmune condition where pancreas cannot produce insulin. Usually diagnosed in children and young adults. Requires insulin therapy for survival.
Type 2 Diabetes: Most common form, accounting for 90% of cases. Related to insulin resistance and lifestyle factors. Can often be managed with diet, exercise, and medications.
Gestational Diabetes: Occurs during pregnancy and increases risk of Type 2 diabetes later.
Symptoms include excessive thirst, frequent urination, fatigue, blurred vision, and slow healing wounds.
Diagnosis involves blood glucose tests, HbA1c test, and oral glucose tolerance test.
Management includes blood sugar monitoring, medication, diet control, regular exercise, and foot care.
Complications include heart disease, stroke, kidney disease, diabetic retinopathy, and neuropathy.
Prevention in Type 2 involves weight management, physical activity, and healthy diet.
Regular check-ups with endocrinologist are recommended for optimal control.""",
            "metadata": {"source": "diabetes_guide.txt", "topic": "medical"}
        },
        {
            "content": """Heart Disease and Cardiac Conditions:
Coronary Artery Disease (CAD) is the most common type of heart disease.
It occurs when plaque builds up in coronary arteries, reducing blood flow to the heart.
Risk factors include high blood pressure, high cholesterol, smoking, diabetes, obesity, and family history.
Symptoms may include chest pain (angina), shortness of breath, and heart attack warning signs.
Heart attack symptoms include severe chest pain, arm pain, jaw pain, nausea, and sweating.
Treatment includes medications, lifestyle changes, and procedures like angioplasty or bypass surgery.
Atrial Fibrillation (AFib) is an irregular heartbeat that increases stroke risk.
Heart failure occurs when the heart cannot pump blood effectively.
Valve diseases affect the heart's one-way valves.
Prevention involves maintaining healthy weight, not smoking, managing stress, and regular exercise.
Warning signs require immediate medical attention and emergency care.""",
            "metadata": {"source": "heart_disease_guide.txt", "topic": "medical"}
        },
        {
            "content": """About MediCare Elite Hospital Bangalore:
MediCare Elite Hospital is a fictional premium healthcare facility located at Electronic City Phase 2, Bangalore.
Establishment: Founded in January 2025.
Address: Plot 42, Sector 7, Electronic City Phase 2, Bangalore - 560100.
Contact: +91-80-4567-8900.
Email: contact@medicareelite.in.
Website: www.medicareelite.in.
Specializations: Cardiology Department headed by Dr. Rajesh Kumar (20 years experience), Neurology Department headed by Dr. Priya Sharma (15 years experience), Orthopedics headed by Dr. Amit Patel (18 years experience), Endocrinology Department for Diabetes Management, Nephrology for Kidney Diseases.
Facilities: 24/7 Emergency with air-conditioned ambulances, 150-bed capacity including 30 ICU beds, 5 state-of-the-art operation theatres, In-house pharmacy and diagnostic center, Free WiFi for all patients, Cafeteria with healthy food options.
Unique Features: First hospital in Bangalore with AI-powered diagnosis system, Rooftop helipad for emergency air ambulance, Dedicated COVID-19 isolation ward with 25 beds, Mobile app "MediCare Connect" for appointment booking, Telemedicine services available, Patient education programs, Support groups for chronic diseases.""",
            "metadata": {"source": "medicare_elite_hospital.txt", "topic": "hospital"}
        },
        {
            "content": """MediCare Elite Hospital - Department of Cardiology:
Head of Department: Dr. Rajesh Kumar, MD, DM (Cardiology).
20 years of experience in interventional cardiology.
Trained at Johns Hopkins Hospital, USA.
Performed over 5,000 angioplasty procedures.
Specializes in complex coronary interventions and arrhythmia management.
Department Statistics: 500+ cardiac procedures performed monthly, 95% success rate in emergency angioplasty, Average waiting time for OPD: 30 minutes, Emergency response time: Under 10 minutes.
Equipment: Latest Siemens Artis Zee Cath Lab with AI assistance, 3D Echocardiography machines (2 units), Cardiac CT Scanner - GE Revolution 256-slice, 24/7 ECG monitoring in all cardiac beds, Advanced stress testing equipment.
Special Programs: Free heart health checkup every Sunday from 9 AM - 12 PM, Cardiac rehabilitation program with 6-month follow-up, School heart screening program (screening 500+ students monthly), Diabetes-Heart Disease Management Clinic (Wednesdays), Post-MI support group, Lifestyle modification program.
Consultation Timings: Dr. Rajesh Kumar: Monday to Friday, 10 AM - 1 PM, 4 PM - 7 PM. Dr. Anita Desai (Associate): Monday to Saturday, 9 AM - 2 PM. Emergency Cardiology: 24/7 with on-call cardiologist.
Consultation Fees: First consultation: ₹800, Follow-up: ₹500, Emergency consultation: ₹1,500.""",
            "metadata": {"source": "medicare_cardiology.txt", "topic": "cardiology"}
        },
        {
            "content": """MediCare Elite Hospital - Department of Endocrinology (Diabetes & Metabolic Disorders):
Head of Department: Dr. Sneha Mehta, MD, DM (Endocrinology).
15 years of experience in diabetes management and metabolic disorders.
Specializes in insulin therapy, Type 1 and Type 2 diabetes, PCOS, and thyroid disorders.
Department Statistics: 300+ diabetes patients managed monthly, 90% HbA1c control rate, Average consultation time: 45 minutes.
Services: Type 1 & Type 2 Diabetes Management, Gestational Diabetes Screening and Management, Thyroid Disorders (Hyperthyroidism, Hypothyroidism), Polycystic Ovary Syndrome (PCOS), Obesity Management, Metabolic Syndrome Management.
Equipment: Advanced glucose monitoring devices, Continuous Glucose Monitoring (CGM) systems, Insulin pump therapy, Thyroid ultrasound machine.
Special Programs: Diabetes Education Classes (twice weekly), Nutrition Counseling, Diabetes Support Groups, Insulin Training Workshops, Lifestyle Modification Program for Weight Management, PCOS Management Program.
Consultation Timings: Dr. Sneha Mehta: Tuesday to Saturday, 10 AM - 1 PM, 3 PM - 6 PM. Dr. Vikram Singh (Associate): Monday to Friday, 2 PM - 5 PM.
Consultation Fees: First consultation: ₹600, Follow-up: ₹400, Group sessions: ₹200 per person.""",
            "metadata": {"source": "medicare_endocrinology.txt", "topic": "endocrinology"}
        },
        {
            "content": """MediCare Elite Hospital - Patient Services & Appointment System:
ONLINE APPOINTMENT BOOKING: Book through "MediCare Connect" app (Available on iOS and Android), Select department and doctor, Choose preferred time slot from available options, Pay ₹200 booking fee online (refundable), Get instant confirmation SMS, Receive reminder notification 1 hour before appointment, Reschedule or cancel anytime.
WALK-IN REGISTRATION: Reception Counter at Ground Floor, Timing 8 AM - 8 PM daily (including weekends), Token system for walk-in patients, Average wait time: 45 minutes, Priority given to emergency cases.
EMERGENCY SERVICES: 24/7 Emergency Department with dedicated trauma center, Direct admission without appointment for emergencies, Fully equipped ambulance with advanced life support, Paramedics available for on-site assistance, Emergency hotline: +91-80-4567-9911, Average response time: 10 minutes.
TELEMEDICINE SERVICES: Video consultations with doctors, Available for follow-ups and non-emergency cases, Prescription delivery to home, Report access through app.
INPATIENT FACILITIES: Private and semi-private rooms, Room service with nutritious meals, 24/7 nursing care, WiFi and entertainment facilities, Visitor guidelines and timings.""",
            "metadata": {"source": "medicare_services.txt", "topic": "services"}
        },
        {
            "content": """MediCare Elite Hospital - Health Packages and Pricing:
BASIC HEALTH CHECKUP PACKAGE: ₹2,999. Includes: Complete Blood Count (CBC), Lipid Profile (Cholesterol, Triglycerides), Blood Sugar (Fasting and Post-meal), Kidney Function Tests (Creatinine, BUN, eGFR), Liver Function Tests (Bilirubin, Albumin, AST, ALT), Thyroid Function (TSH), Electrocardiogram (ECG), Doctor Consultation and Health Report.
CARDIAC HEALTH PACKAGE: ₹5,999. Includes: All Basic tests, 2D Echocardiography (heart ultrasound), TMT (Treadmill Test), Holter Monitor (24-hour ECG), Cardiologist Consultation, Dietary Chart for Heart Health, Follow-up appointment.
DIABETES MANAGEMENT PACKAGE: ₹4,499. Includes: Fasting Blood Sugar, Post-meal Blood Sugar, HbA1c (3-month glucose average), Kidney Function Test (for diabetes complications), Eye Checkup with Retinopathy Screening, Foot Examination, Endocrinologist Consultation, Diabetic Diet Plan, Diabetes Education Session.
WELLNESS PACKAGE: ₹3,499. Includes: All Basic tests, BMI and Body Composition Analysis, Fitness Assessment, Nutritionist Consultation, Mental Health Screening, Stress Management Session, Lifestyle Counseling.
SENIOR CITIZEN PACKAGE (Age 60+): ₹6,999. Includes: All Basic tests, Cardiac evaluation, Bone density scan, Memory assessment, Vision and Hearing tests, Senior Physician Consultation, Comprehensive Health Report.
CORPORATE PACKAGES: Bulk discounts available (5+ employees). Onsite health camps, Regular follow-up programs, Employee wellness programs.""",
            "metadata": {"source": "medicare_packages.txt", "topic": "services"}
        },
        {
            "content": """MediCare Elite Hospital - Insurance and Payment Options:
INSURANCE ACCEPTED: All major health insurance companies (ICICI Lombard, HDFC Ergo, Apollo DKV, Star Health, Max Bupa, Aditya Birla Health, Royal Sundaram).
INSURANCE FEATURES: Cashless facility available at our center, Direct billing to insurance company, Pre-authorization support, Claim assistance by dedicated staff, Network hospital for major insurers.
GOVERNMENT SCHEMES: Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (PM-JAY), Karnataka Arogya scheme, RSBY (Rajiv Gandhi Scheme for Vulnerable Groups).
INTERNATIONAL INSURANCE: Accepts international health insurance through Third Party Administrator (TPA), Coverage for international patients, Multilingual staff available.
PAYMENT METHODS: Cash (at reception), Credit Card (Visa, Mastercard, Amex), Debit Card (all banks), UPI (Google Pay, PhonePe, Paytm), Net Banking (all major banks), Cheque (for advance payments).
MEDICAL LOANS: Available through Bajaj Finserv (0% interest for 3 months), ICICI Personal Loans for medical procedures, SBI healthcare loans.
EMI OPTIONS: Available for surgeries and procedures above ₹50,000, Flexible payment plans (3, 6, 12 months), No processing fee for hospital procedures.
DISCOUNTS: Senior citizen discount (5%), Group discount (3% for family packages), Referral bonus (₹500 for successful referral), Loyalty program for regular patients.""",
            "metadata": {"source": "medicare_insurance.txt", "topic": "services"}
        }
    ]

    doc_num = 1
    total_chunks = 0

    for doc in documents:
        # Chunk the document with smaller chunk size for more chunks
        chunks = chunk_document(doc["content"], chunk_size=250, overlap=40)

        print(f"\nDocument {doc_num}: {doc['metadata']['source']}")
        print(f"Split into {len(chunks)} chunks")

        # Add each chunk separately
        for chunk_idx, chunk in enumerate(chunks):
            try:
                vector_store.add_document(
                    content=chunk,
                    metadata={
                        "source": doc["metadata"]["source"],
                        "topic": doc["metadata"]["topic"],
                        "chunk_id": chunk_idx
                    }
                )
                print(f"  ✓ Added chunk {chunk_idx + 1}/{len(chunks)} ({len(chunk)} chars)")
                total_chunks += 1
            except Exception as e:
                print(f"  ✗ Error adding chunk {chunk_idx}: {e}")

        doc_num += 1

    db.close()
    print("\n" + "=" * 60)
    print(f"ALL DOCUMENTS CHUNKED AND ADDED SUCCESSFULLY!")
    print(f"Total chunks created: {total_chunks}")
    print("=" * 60)


if __name__ == "__main__":
    print("WARNING: This will DELETE all existing documents!")
    print("This adds FICTIONAL hospital data with chunking.")
    print("Are you sure? (yes/no): ", end="")

    if input().strip().lower() == "yes":
        clear_and_add_test_hospital()
    else:
        print("Cancelled.")