from app.core.database import SessionLocal
from app.models.document import Document
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

model = SentenceTransformer("all-MiniLM-L6-v2")


def add_documents():
    db = SessionLocal()

    logger.info("=" * 60)
    logger.info("ADDING MEDICAL DOCUMENTS WITH EMBEDDINGS")
    logger.info("=" * 60)

    try:
        count = db.query(Document).count()
        logger.info(f"Found {count} existing documents")

        db.query(Document).delete()
        db.commit()
        logger.info("Documents cleared")
    except Exception:
        logger.exception("Failed to clear documents")
        db.rollback()
        db.close()
        return

    documents = [
        # Consultation Fees
        "Cardiology consultation fee is ₹800 for first visit and ₹500 for follow-up.",
        "General physician consultation fee is ₹500.",
        "Pediatrician consultation fee is ₹600 for first visit and ₹400 for follow-up.",
        "Dermatologist consultation fee is ₹700 for first visit and ₹450 for follow-up.",
        "Orthopedic consultation fee is ₹900 for first visit and ₹600 for follow-up.",
        "Neurologist consultation fee is ₹1000 for first visit and ₹700 for follow-up.",
        "Gynecologist consultation fee is ₹750 for first visit and ₹500 for follow-up.",
        "ENT specialist consultation fee is ₹650 for first visit and ₹450 for follow-up.",
        "Ophthalmologist consultation fee is ₹600 for first visit and ₹400 for follow-up.",
        "Psychiatrist consultation fee is ₹1200 for first visit and ₹800 for follow-up.",
        "Dentist consultation fee is ₹500 for checkup and ₹800 for procedures.",
        "Urologist consultation fee is ₹850 for first visit and ₹550 for follow-up.",

        # Diagnostic Tests - Imaging
        "MRI scan costs range from ₹4500 to ₹8000 depending on body part.",
        "CT scan costs approximately ₹3000 to ₹6000.",
        "X-ray costs ₹250 to ₹500 depending on area.",
        "Ultrasound scan costs ₹1500 to ₹2500.",
        "Mammography costs ₹2000 to ₹3000.",
        "PET scan costs ₹18000 to ₹25000.",
        "Bone density scan (DEXA) costs ₹2500 to ₹3500.",
        "3D/4D ultrasound costs ₹3000 to ₹5000.",

        # Diagnostic Tests - Cardiology
        "ECG test costs ₹300 to ₹500.",
        "2D Echo (Echocardiogram) costs ₹2000 to ₹3000.",
        "Stress test (TMT) costs ₹2500 to ₹3500.",
        "Holter monitoring (24-hour) costs ₹3000 to ₹4000.",

        # Blood Tests
        "Blood test packages start from ₹1200.",
        "Complete blood count (CBC) costs ₹300 to ₹500.",
        "Lipid profile test costs ₹600 to ₹800.",
        "Liver function test (LFT) costs ₹700 to ₹900.",
        "Kidney function test (KFT) costs ₹700 to ₹900.",
        "Thyroid profile (T3, T4, TSH) costs ₹800 to ₹1200.",
        "HbA1c (Diabetes) test costs ₹400 to ₹600.",
        "Vitamin D test costs ₹1200 to ₹1800.",
        "Vitamin B12 test costs ₹800 to ₹1200.",
        "Iron profile test costs ₹1000 to ₹1500.",
        "Covid-19 RT-PCR test costs ₹500 to ₹800.",
        "Covid-19 Rapid Antigen test costs ₹300 to ₹500.",

        # Therapy & Rehabilitation
        "Physiotherapy session costs ₹700 per session.",
        "Occupational therapy costs ₹800 per session.",
        "Speech therapy costs ₹900 per session.",
        "Psychological counseling costs ₹1500 per session.",
        "Couples therapy costs ₹2500 per session.",
        "Family therapy costs ₹3000 per session.",

        # Surgical Procedures
        "Appendectomy surgery costs ₹40000 to ₹80000.",
        "Cataract surgery costs ₹25000 to ₹50000 per eye.",
        "Hernia repair surgery costs ₹50000 to ₹100000.",
        "Gallbladder removal surgery costs ₹60000 to ₹120000.",
        "Knee replacement surgery costs ₹200000 to ₹400000.",
        "Hip replacement surgery costs ₹250000 to ₹500000.",
        "Cesarean delivery costs ₹50000 to ₹150000.",
        "Normal delivery costs ₹30000 to ₹80000.",

        # Dental Procedures
        "Teeth cleaning costs ₹1000 to ₹2000.",
        "Tooth filling costs ₹800 to ₹2000 per tooth.",
        "Root canal treatment costs ₹3000 to ₹8000 per tooth.",
        "Tooth extraction costs ₹500 to ₹2000.",
        "Dental implant costs ₹25000 to ₹50000 per tooth.",
        "Teeth whitening costs ₹8000 to ₹15000.",
        "Braces (orthodontic treatment) costs ₹40000 to ₹100000.",

        # Vaccination
        "Flu vaccine costs ₹500 to ₹800.",
        "Hepatitis B vaccine costs ₹300 to ₹500 per dose.",
        "Tetanus vaccine costs ₹200 to ₹400.",
        "HPV vaccine costs ₹3000 to ₹4000 per dose.",
        "Pneumonia vaccine costs ₹3500 to ₹5000.",
        "Chickenpox vaccine costs ₹1500 to ₹2500.",

        # Emergency Services
        "Emergency room visit costs ₹2000 to ₹5000.",
        "Ambulance service costs ₹1000 to ₹3000 depending on distance.",
        "ICU charges are ₹8000 to ₹15000 per day.",
        "General ward bed costs ₹2000 to ₹4000 per day.",
        "Private room costs ₹5000 to ₹10000 per day.",

        # Health Packages
        "Basic health checkup package costs ₹2500 to ₹4000.",
        "Comprehensive health checkup costs ₹8000 to ₹12000.",
        "Executive health checkup costs ₹15000 to ₹25000.",
        "Cardiac health package costs ₹6000 to ₹10000.",
        "Diabetic health package costs ₹5000 to ₹8000.",
        "Women's health package costs ₹7000 to ₹12000.",
        "Men's health package costs ₹7000 to ₹12000.",
        "Senior citizen health package costs ₹10000 to ₹15000.",

        # Specialized Tests
        "Biopsy costs ₹3000 to ₹8000.",
        "Endoscopy costs ₹5000 to ₹10000.",
        "Colonoscopy costs ₹8000 to ₹15000.",
        "Bronchoscopy costs ₹8000 to ₹12000.",
        "Sleep study (Polysomnography) costs ₹8000 to ₹15000.",
        "Allergy test panel costs ₹5000 to ₹10000.",
        "Genetic testing costs ₹15000 to ₹50000.",

        # Hospital Services
        "Hospital registration fee is ₹200 to ₹500.",
        "Medical certificate costs ₹200 to ₹500.",
        "Prescription costs ₹100 to ₹300.",
        "Home visit by doctor costs ₹1500 to ₹3000.",
        "Telemedicine consultation costs ₹300 to ₹500.",

        # Insurance Information
        "Health insurance cashless facility available for all major insurers.",
        "Mediclaim accepted for hospitalization above 24 hours.",
        "Corporate health insurance tie-ups available.",
        "Government health schemes (Ayushman Bharat) accepted.",

        # Hospital Timings
        "OPD timings are Monday to Saturday 9 AM to 5 PM.",
        "Emergency services available 24/7.",
        "Blood bank operates 24/7.",
        "Pharmacy open 24/7.",
        "Diagnostic center operates from 7 AM to 9 PM.",

        # Appointment Information
        "Appointments can be booked online or by calling reception.",
        "Walk-in patients accepted based on availability.",
        "Average waiting time for consultation is 20-30 minutes.",
        "Priority appointments available for senior citizens and pregnant women.",
        "Follow-up appointments should be scheduled within recommended timeframe.",
    ]

    logger.info("Generating embeddings...")
    embeddings = model.encode(documents, show_progress_bar=True)

    for i, (content, embedding) in enumerate(zip(documents, embeddings), start=1):
        try:
            doc = Document(
                content=content,
                embedding=embedding.tolist()
            )
            db.add(doc)
            logger.info(f"Inserted document {i}")
        except Exception:
            logger.exception(f"Failed on document {i}")
            db.rollback()
            db.close()
            return

    db.commit()
    db.close()

    logger.info("=" * 60)
    logger.info(f"✅ DOCUMENT INGESTION COMPLETE - {len(documents)} documents added")
    logger.info("=" * 60)


if __name__ == "__main__":
    confirm = input("Type YES to rebuild document store: ").strip()
    if confirm == "YES":
        add_documents()
    else:
        print("Cancelled.")